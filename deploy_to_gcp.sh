#!/bin/bash

###############################################################################
# Cloud Brain GCP Deployment Script
# Automates deployment of Cloud Brain system to Google Cloud Platform
###############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ID="${CLOUD_BRAIN_PROJECT_ID:-}"
REGION="${CLOUD_BRAIN_REGION:-us-central1}"
INSTANCE_NAME="${CLOUD_BRAIN_INSTANCE_NAME:-cloudbrain-db}"
DB_NAME="${CLOUD_BRAIN_DB_NAME:-cloudbrain}"
DB_USER="${CLOUD_BRAIN_DB_USER:-cloudbrain}"
DB_PASSWORD="${CLOUD_BRAIN_DB_PASSWORD:-}"
DB_TIER="${CLOUD_BRAIN_DB_TIER:-db-f1-micro}"
STORAGE_SIZE="${CLOUD_BRAIN_STORAGE_SIZE:-10}"

###############################################################################
# Helper Functions
###############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_gcloud_installed() {
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first:"
        echo "  https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    log_success "gcloud CLI is installed"
}

check_gcloud_auth() {
    log_info "Checking gcloud authentication..."
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        log_error "Not authenticated with gcloud. Please run: gcloud auth login"
        exit 1
    fi
    log_success "Authenticated with gcloud"
}

set_project() {
    if [[ -z "$PROJECT_ID" ]]; then
        log_error "PROJECT_ID is not set. Please set CLOUD_BRAIN_PROJECT_ID environment variable"
        exit 1
    fi
    
    log_info "Setting project to: $PROJECT_ID"
    gcloud config set project "$PROJECT_ID"
    log_success "Project set to $PROJECT_ID"
}

enable_apis() {
    log_info "Enabling required GCP APIs..."
    
    gcloud services enable sqladmin.googleapis.com \
        cloudresourcemanager.googleapis.com \
        iam.googleapis.com \
        secretmanager.googleapis.com \
        --project="$PROJECT_ID"
    
    log_success "Required APIs enabled"
}

create_cloud_sql_instance() {
    log_info "Creating Cloud SQL PostgreSQL instance..."
    
    # Check if instance already exists
    if gcloud sql instances list --filter="name:$INSTANCE_NAME" --format="value(name)" | grep -q "$INSTANCE_NAME"; then
        log_warning "Cloud SQL instance '$INSTANCE_NAME' already exists. Skipping creation."
        return 0
    fi
    
    gcloud sql instances create "$INSTANCE_NAME" \
        --database-version=POSTGRES_14 \
        --tier="$DB_TIER" \
        --storage-size="$STORAGE_SIZE" \
        --region="$REGION" \
        --database-flags="cloudsql.iam_authentication=On" \
        --project="$PROJECT_ID"
    
    log_success "Cloud SQL instance '$INSTANCE_NAME' created"
}

create_database() {
    log_info "Creating database '$DB_NAME'..."
    
    gcloud sql databases create "$DB_NAME" \
        --instance="$INSTANCE_NAME" \
        --project="$PROJECT_ID"
    
    log_success "Database '$DB_NAME' created"
}

create_database_user() {
    log_info "Creating database user '$DB_USER'..."
    
    if [[ -z "$DB_PASSWORD" ]]; then
        log_error "DB_PASSWORD is not set. Please set CLOUD_BRAIN_DB_PASSWORD environment variable"
        exit 1
    fi
    
    gcloud sql users create "$DB_USER" \
        --instance="$INSTANCE_NAME" \
        --password="$DB_PASSWORD" \
        --project="$PROJECT_ID"
    
    log_success "Database user '$DB_USER' created"
}

get_connection_string() {
    log_info "Getting connection string..."
    
    CONNECTION_NAME=$(gcloud sql instances describe "$INSTANCE_NAME" \
        --format="value(connectionName)" \
        --project="$PROJECT_ID")
    
    CONNECTION_STRING="host=/cloudsql/$CONNECTION_NAME dbname=$DB_NAME user=$DB_USER password=$DB_PASSWORD"
    
    echo "$CONNECTION_STRING"
}

wait_for_instance() {
    log_info "Waiting for Cloud SQL instance to be ready..."
    
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        STATE=$(gcloud sql instances describe "$INSTANCE_NAME" \
            --format="value(state)" \
            --project="$PROJECT_ID" 2>/dev/null || echo "UNKNOWN")
        
        if [[ "$STATE" == "RUNNABLE" ]]; then
            log_success "Cloud SQL instance is ready"
            return 0
        fi
        
        attempt=$((attempt + 1))
        log_info "Waiting for instance... (attempt $attempt/$max_attempts, state: $STATE)"
        sleep 10
    done
    
    log_error "Cloud SQL instance did not become ready in time"
    exit 1
}

###############################################################################
# Database Migration Functions
###############################################################################

install_dependencies() {
    log_info "Installing Python dependencies..."
    
    pip3 install --quiet \
        psycopg2-binary \
        python-dotenv
    
    log_success "Dependencies installed"
}

migrate_database() {
    local connection_string="$1"
    
    log_info "Migrating database from SQLite to PostgreSQL..."
    
    python3 "$SCRIPT_DIR/migrate_to_postgres.py" \
        --sqlite-path "$SCRIPT_DIR/ai_db/cloudbrain.db" \
        --postgres-connection "$connection_string"
    
    log_success "Database migration completed"
}

###############################################################################
# Deployment Functions
###############################################################################

deploy_application() {
    log_info "Deploying Cloud Brain application..."
    
    # Create deployment directory
    local deploy_dir="/tmp/cloudbrain-deploy"
    rm -rf "$deploy_dir"
    mkdir -p "$deploy_dir"
    
    # Copy necessary files
    cp -r "$SCRIPT_DIR"/* "$deploy_dir/"
    
    # Create environment file
    cat > "$deploy_dir/.env" << EOF
CLOUD_BRAIN_DB_TYPE=postgresql
CLOUD_BRAIN_CONNECTION_STRING=$connection_string
CLOUD_BRAIN_PROJECT_ID=$PROJECT_ID
CLOUD_BRAIN_REGION=$REGION
CLOUD_BRAIN_INSTANCE_NAME=$INSTANCE_NAME
EOF
    
    log_success "Application prepared for deployment"
    echo "Deployment directory: $deploy_dir"
}

###############################################################################
# Verification Functions
###############################################################################

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Test database connection
    python3 "$SCRIPT_DIR/verify_deployment.py" \
        --connection-string "$connection_string"
    
    log_success "Deployment verified successfully"
}

###############################################################################
# Rollback Functions
###############################################################################

rollback_deployment() {
    log_warning "Rolling back deployment..."
    
    # This would restore from backup or revert changes
    # Implementation depends on your backup strategy
    
    log_warning "Rollback completed"
}

###############################################################################
# Main Deployment Flow
###############################################################################

main() {
    log_info "Starting Cloud Brain GCP deployment..."
    echo ""
    
    # Pre-deployment checks
    check_gcloud_installed
    check_gcloud_auth
    set_project
    enable_apis
    
    # Create GCP resources
    create_cloud_sql_instance
    wait_for_instance
    create_database
    create_database_user
    
    # Get connection string
    CONNECTION_STRING=$(get_connection_string)
    log_info "Connection string: [REDACTED]"
    
    # Migrate database
    install_dependencies
    migrate_database "$CONNECTION_STRING"
    
    # Deploy application
    deploy_application
    
    # Verify deployment
    verify_deployment
    
    echo ""
    log_success "Cloud Brain deployment completed successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Update your application to use the PostgreSQL connection string"
    echo "  2. Test the application with the new cloud database"
    echo "  3. Monitor the Cloud SQL instance in GCP Console"
    echo ""
    echo "Connection string (save securely):"
    echo "  $CONNECTION_STRING"
    echo ""
    echo "Cloud SQL instance details:"
    gcloud sql instances describe "$INSTANCE_NAME" --project="$PROJECT_ID"
}

###############################################################################
# Script Entry Point
###############################################################################

# Parse command line arguments
case "${1:-deploy}" in
    deploy)
        main
        ;;
    rollback)
        rollback_deployment
        ;;
    verify)
        verify_deployment
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|verify}"
        echo ""
        echo "Environment variables:"
        echo "  CLOUD_BRAIN_PROJECT_ID      - GCP Project ID (required)"
        echo "  CLOUD_BRAIN_REGION          - GCP Region (default: us-central1)"
        echo "  CLOUD_BRAIN_INSTANCE_NAME    - Cloud SQL instance name (default: cloudbrain-db)"
        echo "  CLOUD_BRAIN_DB_NAME         - Database name (default: cloudbrain)"
        echo "  CLOUD_BRAIN_DB_USER         - Database user (default: cloudbrain)"
        echo "  CLOUD_BRAIN_DB_PASSWORD     - Database password (required)"
        echo "  CLOUD_BRAIN_DB_TIER        - Database tier (default: db-f1-micro)"
        echo "  CLOUD_BRAIN_STORAGE_SIZE     - Storage size in GB (default: 10)"
        exit 1
        ;;
esac
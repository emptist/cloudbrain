#!/bin/bash

###############################################################################
# Cloud Brain GCP Setup Script
# Automates the setup of Google Cloud Platform for Cloud Brain deployment
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ID="${CLOUD_BRAIN_PROJECT_ID:-cloudbrain}"
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
        echo ""
        echo "On macOS with Homebrew:"
        echo "  brew install google-cloud-sdk"
        echo ""
        echo "Or download from:"
        echo "  https://cloud.google.com/cli/docs/install"
        exit 1
    fi
    log_success "gcloud CLI is installed"
}

check_gcloud_auth() {
    log_info "Checking gcloud authentication..."
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        log_warning "Not authenticated with gcloud. Please run: gcloud auth login"
        read -p "Would you like to authenticate now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            gcloud auth login
        else
            exit 1
        fi
    fi
    log_success "Authenticated with gcloud"
}

create_project() {
    log_info "Creating GCP project: $PROJECT_ID"
    
    # Check if project already exists
    if gcloud projects list --filter="project_id:$PROJECT_ID" --format="value(project_id)" | grep -q "$PROJECT_ID"; then
        log_warning "Project '$PROJECT_ID' already exists. Skipping creation."
        return 0
    fi
    
    # Create project
    gcloud projects create "$PROJECT_ID" --name="Cloud Brain AI"
    
    # Set as default
    gcloud config set project "$PROJECT_ID"
    
    log_success "Project '$PROJECT_ID' created and set as default"
}

enable_apis() {
    log_info "Enabling required GCP APIs..."
    
    gcloud services enable \
        sqladmin.googleapis.com \
        cloudresourcemanager.googleapis.com \
        iam.googleapis.com \
        secretmanager.googleapis.com \
        --project="$PROJECT_ID"
    
    log_success "Required APIs enabled"
}

create_service_account() {
    log_info "Creating service account: cloudbrain-deployer"
    
    local service_account="cloudbrain-deployer@$PROJECT_ID.iam.gserviceaccount.com"
    
    # Check if service account already exists
    if gcloud iam service-accounts list --filter="email:$service_account" --format="value(email)" | grep -q "$service_account"; then
        log_warning "Service account already exists. Skipping creation."
        return 0
    fi
    
    # Create service account
    gcloud iam service-accounts create cloudbrain-deployer \
        --display-name="Cloud Brain Deployer" \
        --description="Service account for Cloud Brain deployment" \
        --project="$PROJECT_ID"
    
    log_success "Service account created"
}

grant_permissions() {
    log_info "Granting permissions to service account..."
    
    local service_account="cloudbrain-deployer@$PROJECT_ID.iam.gserviceaccount.com"
    
    # Grant Cloud SQL Admin role
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$service_account" \
        --role="roles/cloudsql.admin" \
        --project="$PROJECT_ID" 2>/dev/null || true
    
    # Grant Service Usage Admin role
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$service_account" \
        --role="roles/serviceusage.serviceUsageAdmin" \
        --project="$PROJECT_ID" 2>/dev/null || true
    
    # Grant Cloud Resource Manager role
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$service_account" \
        --role="roles/resourcemanager.projectIamAdmin" \
        --project="$PROJECT_ID" 2>/dev/null || true
    
    # Grant Compute Admin role
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$service_account" \
        --role="roles/compute.admin" \
        --project="$PROJECT_ID" 2>/dev/null || true
    
    log_success "Permissions granted"
}

create_service_account_key() {
    log_info "Creating service account key..."
    
    local service_account="cloudbrain-deployer@$PROJECT_ID.iam.gserviceaccount.com"
    local credentials_dir="$HOME/.gcp-credentials"
    local credentials_file="$credentials_dir/cloudbrain-deployer.json"
    
    # Create credentials directory
    mkdir -p "$credentials_dir"
    
    # Create key
    gcloud iam service-accounts keys create "$credentials_file" \
        --iam-account="$service_account" \
        --project="$PROJECT_ID"
    
    # Set secure permissions
    chmod 600 "$credentials_file"
    
    log_success "Service account key created: $credentials_file"
    log_warning "⚠️  Keep this file secure! Never commit it to version control."
    
    echo ""
    echo "Credentials file location: $credentials_file"
    echo ""
    echo "To add this to GitHub Secrets:"
    echo "  1. Copy the contents of the file:"
    echo "     cat $credentials_file"
    echo "  2. Go to GitHub → Settings → Secrets and variables → Actions"
    echo "  3. Create a new secret named 'GCP_CREDENTIALS'"
    echo "  4. Paste the JSON content"
}

generate_password() {
    log_info "Generating secure database password..."
    
    if [[ -z "$DB_PASSWORD" ]]; then
        DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    fi
    
    log_success "Database password generated"
    echo ""
    echo "Database Password: $DB_PASSWORD"
    echo ""
    log_warning "⚠️  Save this password securely!"
}

create_env_file() {
    log_info "Creating .env file..."
    
    local env_file="$SCRIPT_DIR/.env"
    
    # Check if .env already exists
    if [[ -f "$env_file" ]]; then
        log_warning ".env file already exists. Skipping creation."
        return 0
    fi
    
    # Create .env file
    cat > "$env_file" << EOF
# Cloud Brain GCP Configuration
# Generated by setup_gcp.sh

# GCP Project Configuration
CLOUD_BRAIN_PROJECT_ID=$PROJECT_ID
CLOUD_BRAIN_REGION=$REGION

# Cloud SQL Instance Configuration
CLOUD_BRAIN_INSTANCE_NAME=$INSTANCE_NAME
CLOUD_BRAIN_DB_NAME=$DB_NAME
CLOUD_BRAIN_DB_USER=$DB_USER
CLOUD_BRAIN_DB_PASSWORD=$DB_PASSWORD

# Database Configuration
CLOUD_BRAIN_DB_TYPE=postgresql
CLOUD_BRAIN_DB_TIER=$DB_TIER
CLOUD_BRAIN_STORAGE_SIZE=$STORAGE_SIZE

# AI Configuration
CLOUD_BRAIN_AI_ID=1
CLOUD_BRAIN_AI_NAME=AI_Assistant

# Development Settings
CLOUD_BRAIN_ENVIRONMENT=development
CLOUD_BRAIN_DEBUG=false
EOF
    
    log_success ".env file created: $env_file"
    log_warning "⚠️  Make sure to add .env to .gitignore!"
}

print_github_secrets() {
    echo ""
    echo "=========================================="
    echo "GitHub Secrets Configuration"
    echo "=========================================="
    echo ""
    echo "Add these secrets to your GitHub repository:"
    echo "  Go to: Settings → Secrets and variables → Actions"
    echo ""
    echo "Required Secrets:"
    echo ""
    echo "  GCP_CREDENTIALS"
    echo "    Value: Contents of ~/.gcp-credentials/cloudbrain-deployer.json"
    echo ""
    echo "  GCP_PROJECT_ID"
    echo "    Value: $PROJECT_ID"
    echo ""
    echo "  GCP_REGION"
    echo "    Value: $REGION"
    echo ""
    echo "  GCP_INSTANCE_NAME"
    echo "    Value: $INSTANCE_NAME"
    echo ""
    echo "  GCP_DB_NAME"
    echo "    Value: $DB_NAME"
    echo ""
    echo "  GCP_DB_USER"
    echo "    Value: $DB_USER"
    echo ""
    echo "  GCP_DB_PASSWORD"
    echo "    Value: $DB_PASSWORD"
    echo ""
    echo "  GCP_DB_TIER"
    echo "    Value: $DB_TIER"
    echo ""
    echo "  GCP_STORAGE_SIZE"
    echo "    Value: $STORAGE_SIZE"
    echo ""
    echo "=========================================="
}

print_next_steps() {
    echo ""
    echo "=========================================="
    echo "Setup Complete!"
    echo "=========================================="
    echo ""
    echo "Next Steps:"
    echo ""
    echo "1. Add secrets to GitHub (see above)"
    echo ""
    echo "2. Deploy to GCP:"
    echo "   ./deploy_to_gcp.sh"
    echo ""
    echo "3. Or push to main branch to trigger GitHub Actions:"
    echo "   git add ."
    echo "   git commit -m 'Deploy Cloud Brain to GCP'"
    echo "   git push origin main"
    echo ""
    echo "4. Monitor deployment in GitHub Actions tab"
    echo ""
    echo "For more information, see: GCP_SETUP_GUIDE.md"
    echo ""
}

###############################################################################
# Main Setup Flow
###############################################################################

main() {
    echo "=========================================="
    echo "Cloud Brain GCP Setup"
    echo "=========================================="
    echo ""
    
    # Check prerequisites
    check_gcloud_installed
    check_gcloud_auth
    
    # Create project
    create_project
    
    # Enable APIs
    enable_apis
    
    # Create service account
    create_service_account
    
    # Grant permissions
    grant_permissions
    
    # Create service account key
    create_service_account_key
    
    # Generate password
    generate_password
    
    # Create .env file
    create_env_file
    
    # Print GitHub secrets configuration
    print_github_secrets
    
    # Print next steps
    print_next_steps
}

###############################################################################
# Script Entry Point
###############################################################################

# Parse command line arguments
case "${1:-setup}" in
    setup)
        main
        ;;
    *)
        echo "Usage: $0 {setup}"
        echo ""
        echo "Environment variables:"
        echo "  CLOUD_BRAIN_PROJECT_ID      - GCP Project ID (default: cloudbrain-ai)"
        echo "  CLOUD_BRAIN_REGION          - GCP Region (default: us-central1)"
        echo "  CLOUD_BRAIN_INSTANCE_NAME    - Cloud SQL instance name (default: cloudbrain-db)"
        echo "  CLOUD_BRAIN_DB_NAME         - Database name (default: cloudbrain)"
        echo "  CLOUD_BRAIN_DB_USER         - Database user (default: cloudbrain)"
        echo "  CLOUD_BRAIN_DB_PASSWORD     - Database password (auto-generated if not set)"
        echo "  CLOUD_BRAIN_DB_TIER        - Database tier (default: db-f1-micro)"
        echo "  CLOUD_BRAIN_STORAGE_SIZE     - Storage size in GB (default: 10)"
        exit 1
        ;;
esac
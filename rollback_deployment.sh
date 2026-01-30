#!/bin/bash

###############################################################################
# Cloud Brain Rollback Script
# Rolls back Cloud Brain deployment to previous state
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
BACKUP_DIR="${CLOUD_BRAIN_BACKUP_DIR:-/tmp/cloudbrain-backups}"
PROJECT_ID="${CLOUD_BRAIN_PROJECT_ID:-}"
REGION="${CLOUD_BRAIN_REGION:-us-central1}"
INSTANCE_NAME="${CLOUD_BRAIN_INSTANCE_NAME:-cloudbrain-db}"
DB_NAME="${CLOUD_BRAIN_DB_NAME:-cloudbrain}"

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
        echo "  https://cloud.google.com/cli/docs/install"
        exit 1
    fi
}

check_gcloud_auth() {
    log_info "Checking gcloud authentication..."
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        log_error "Not authenticated with gcloud. Please run: gcloud auth login"
        exit 1
    fi
}

set_project() {
    if [[ -z "$PROJECT_ID" ]]; then
        log_error "PROJECT_ID is not set. Please set CLOUD_BRAIN_PROJECT_ID environment variable"
        exit 1
    fi
    
    log_info "Setting project to: $PROJECT_ID"
    gcloud config set project "$PROJECT_ID"
}

###############################################################################
# Backup Functions
###############################################################################

create_backup() {
    log_info "Creating backup before rollback..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Create timestamped backup
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/cloudbrain_backup_$timestamp.sql"
    
    # Export database
    log_info "Exporting database to: $backup_file"
    gcloud sql export sql "$INSTANCE_NAME" \
        gs://cloudbrain-backups/backup_$timestamp.sql \
        --project="$PROJECT_ID" \
        --database="$DB_NAME"
    
    log_success "Backup created: $backup_file"
}

list_backups() {
    log_info "Available backups:"
    echo ""
    
    # List backups from GCS
    gsutil ls gs://cloudbrain-backups/ 2>/dev/null || {
        log_warning "No backups found in GCS"
        return 1
    }
    
    # List local backups
    if [[ -d "$BACKUP_DIR" ]]; then
        echo ""
        log_info "Local backups:"
        ls -lh "$BACKUP_DIR"/*.sql 2>/dev/null || log_warning "No local backups found"
    fi
}

###############################################################################
# Rollback Functions
###############################################################################

rollback_database() {
    local backup_file="$1"
    
    if [[ -z "$backup_file" ]]; then
        log_error "Backup file not specified"
        echo "Available backups:"
        list_backups
        exit 1
    fi
    
    log_warning "Rolling back database to: $backup_file"
    echo ""
    log_warning "⚠️  This will replace all current data!"
    echo ""
    
    # Confirm rollback
    read -p "Are you sure you want to rollback? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        log_info "Rollback cancelled"
        exit 0
    fi
    
    # Create backup of current state before rollback
    create_backup
    
    # Import backup
    log_info "Importing backup..."
    
    # Check if backup is local or GCS
    if [[ "$backup_file" == gs://* ]]; then
        # Import from GCS
        gcloud sql import sql "$INSTANCE_NAME" \
            "$backup_file" \
            --project="$PROJECT_ID" \
            --database="$DB_NAME"
    else
        # Import from local file
        gcloud sql import sql "$INSTANCE_NAME" \
            "file://$backup_file" \
            --project="$PROJECT_ID" \
            --database="$DB_NAME"
    fi
    
    log_success "Database rollback completed"
}

rollback_to_timestamp() {
    local timestamp="$1"
    
    log_info "Rolling back to timestamp: $timestamp"
    
    # Find backup for timestamp
    local backup_file=$(ls "$BACKUP_DIR"/*$timestamp*.sql 2>/dev/null | head -1)
    
    if [[ -z "$backup_file" ]]; then
        log_error "No backup found for timestamp: $timestamp"
        list_backups
        exit 1
    fi
    
    rollback_database "$backup_file"
}

rollback_to_previous() {
    log_info "Rolling back to previous backup..."
    
    # Find most recent backup
    local backup_file=$(ls -t "$BACKUP_DIR"/*.sql 2>/dev/null | head -1)
    
    if [[ -z "$backup_file" ]]; then
        log_error "No backups found"
        exit 1
    fi
    
    rollback_database "$backup_file"
}

###############################################################################
# Verification Functions
###############################################################################

verify_rollback() {
    log_info "Verifying rollback..."
    
    # Run verification script
    python3 "$SCRIPT_DIR/scripts/verify_deployment.py" \
        --connection-string "host=/cloudsql/$CONNECTION_NAME dbname=$DB_NAME user=$DB_USER password=$DB_PASSWORD"
    
    log_success "Rollback verified successfully"
}

###############################################################################
# Main Rollback Flow
###############################################################################

main() {
    log_info "Starting Cloud Brain rollback..."
    echo ""
    
    # Pre-rollback checks
    check_gcloud_installed
    check_gcloud_auth
    set_project
    
    # Get connection name
    CONNECTION_NAME=$(gcloud sql instances describe "$INSTANCE_NAME" \
        --format="value(connectionName)" \
        --project="$PROJECT_ID")
    
    # Handle different rollback types
    case "${1:-help}" in
        backup)
            create_backup
            ;;
        
        list)
            list_backups
            ;;
        
        rollback)
            rollback_database "$2"
            verify_rollback
            ;;
        
        rollback-timestamp)
            rollback_to_timestamp "$2"
            verify_rollback
            ;;
        
        rollback-previous)
            rollback_to_previous
            verify_rollback
            ;;
        
        help|*)
            echo "Usage: $0 {backup|list|rollback|rollback-timestamp|rollback-previous|help}"
            echo ""
            echo "Commands:"
            echo "  backup                    - Create a backup before making changes"
            echo "  list                      - List available backups"
            echo "  rollback <backup_file>      - Rollback to specific backup file"
            echo "  rollback-timestamp <time>   - Rollback to backup at timestamp"
            echo "  rollback-previous          - Rollback to most recent backup"
            echo "  help                      - Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  CLOUD_BRAIN_PROJECT_ID      - GCP Project ID (required)"
            echo "  CLOUD_BRAIN_REGION          - GCP Region (default: us-central1)"
            echo "  CLOUD_BRAIN_INSTANCE_NAME    - Cloud SQL instance name"
            echo "  CLOUD_BRAIN_DB_NAME         - Database name"
            echo "  CLOUD_BRAIN_BACKUP_DIR     - Backup directory (default: /tmp/cloudbrain-backups)"
            echo ""
            echo "Examples:"
            echo "  $0 backup                              # Create backup"
            echo "  $0 list                                # List backups"
            echo "  $0 rollback-previous                    # Rollback to previous backup"
            echo "  $0 rollback /tmp/backup_20250130.sql  # Rollback to specific backup"
            echo "  $0 rollback-timestamp 20250130_120000    # Rollback to timestamp"
            exit 1
            ;;
    esac
    
    echo ""
    log_success "Rollback completed!"
    echo ""
    echo "Next steps:"
    echo "  1. Verify application functionality"
    echo "  2. Monitor Cloud SQL instance in GCP Console"
    echo "  3. Create a new backup after verification"
}

###############################################################################
# Script Entry Point
###############################################################################

main "$@"
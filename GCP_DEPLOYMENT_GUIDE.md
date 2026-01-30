# Cloud Brain GCP Deployment Guide

Complete guide for deploying Cloud Brain system to Google Cloud Platform using automated scripts and GitHub Actions.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Setup](#setup)
4. [Automated Deployment via GitHub Actions](#automated-deployment-via-github-actions)
5. [Manual Deployment](#manual-deployment)
6. [Database Migration](#database-migration)
7. [Verification](#verification)
8. [Rollback](#rollback)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## 🎯 Overview

This guide covers deploying the Cloud Brain system to Google Cloud Platform (GCP) using:

- **GitHub Actions** - Fully automated deployment
- **Manual scripts** - Step-by-step deployment
- **Database migration** - SQLite to PostgreSQL
- **Rollback procedures** - Safe recovery from issues

### Deployment Architecture

```
GitHub Repository → GitHub Actions → GCP Cloud SQL → PostgreSQL Database
                                                      ↓
                                              Cloud Brain Application
```

### Components

1. **[deploy_to_gcp.sh](deploy_to_gcp.sh)** - Main deployment script
2. **[.github/workflows/deploy-to-gcp.yml](.github/workflows/deploy-to-gcp.yml)** - GitHub Actions workflow
3. **[scripts/migrate_to_postgres.py](scripts/migrate_to_postgres.py)** - Database migration
4. **[scripts/verify_deployment.py](scripts/verify_deployment.py)** - Deployment verification
5. **[rollback_deployment.sh](rollback_deployment.sh)** - Rollback procedures

## 📦 Prerequisites

### Required Accounts and Services

1. **GitHub Account**
   - Repository with Cloud Brain code
   - Admin access to repository settings

2. **Google Cloud Platform Account**
   - GCP project with billing enabled
   - Permissions to create Cloud SQL instances
   - IAM roles: Cloud SQL Admin, Service Account User

3. **Google Cloud SDK (gcloud)**
   - Install from: https://cloud.google.com/sdk/docs/install
   - Authenticate: `gcloud auth login`

### Required Software

- **Python 3.9+**
  ```bash
  python3 --version
  ```

- **pip (Python package manager)**
  ```bash
  pip3 --version
  ```

- **git** (for GitHub deployment)
  ```bash
  git --version
  ```

### Python Dependencies

Install required packages:
```bash
pip3 install psycopg2-binary python-dotenv google-cloud-sql
```

## ⚙️ Setup

### 1. Configure GCP Project

Set your GCP project ID:
```bash
export CLOUD_BRAIN_PROJECT_ID="your-project-id"
gcloud config set project $CLOUD_BRAIN_PROJECT_ID
```

### 2. Enable Required APIs

```bash
gcloud services enable sqladmin.googleapis.com \
    cloudresourcemanager.googleapis.com \
    iam.googleapis.com \
    secretmanager.googleapis.com \
    --project=$CLOUD_BRAIN_PROJECT_ID
```

### 3. Create Service Account

Create a service account for GitHub Actions:

```bash
gcloud iam service-accounts create cloudbrain-deploy \
    --display-name="Cloud Brain Deployment" \
    --project=$CLOUD_BRAIN_PROJECT_ID
```

Grant necessary roles:
```bash
gcloud projects add-iam-policy-binding $CLOUD_BRAIN_PROJECT_ID \
    --member="serviceAccount:cloudbrain-deploy@$CLOUD_BRAIN_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.admin"
```

### 4. Generate Service Account Key

```bash
gcloud iam service-accounts keys create cloudbrain-deploy \
    --iam-account=cloudbrain-deploy@$CLOUD_BRAIN_PROJECT_ID.iam.gserviceaccount.com \
    --key-file=cloudbrain-deploy-key.json
```

### 5. Configure GitHub Secrets

Add the following secrets to your GitHub repository:

**Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Description | Example |
|-------------|-------------|----------|
| `GCP_PROJECT_ID` | GCP Project ID | `my-cloudbrain-project` |
| `GCP_REGION` | GCP Region | `us-central1` |
| `GCP_INSTANCE_NAME` | Cloud SQL instance name | `cloudbrain-db` |
| `GCP_DB_NAME` | Database name | `cloudbrain` |
| `GCP_DB_USER` | Database user | `cloudbrain` |
| `GCP_DB_PASSWORD` | Database password | `secure-password-123` |
| `GCP_DB_TIER` | Database tier | `db-f1-micro` |
| `GCP_STORAGE_SIZE` | Storage size in GB | `10` |
| `GCP_CREDENTIALS` | Service account key JSON | `{...}` |

**Important:** Use the contents of `cloudbrain-deploy-key.json` for `GCP_CREDENTIALS`.

## 🚀 Automated Deployment via GitHub Actions

### Triggering Deployment

#### Option 1: Push to Main Branch
```bash
git add .
git commit -m "Deploy to GCP"
git push origin main
```

#### Option 2: Manual Trigger
1. Go to: `Actions → Deploy Cloud Brain to GCP`
2. Click: `Run workflow`
3. Select: `environment` (production, staging, development)
4. Click: `Run workflow`

### What Happens During Deployment

1. **Checkout Code** - Pulls latest code from repository
2. **Setup Python** - Configures Python 3.9 environment
3. **Install Dependencies** - Installs required Python packages
4. **Authenticate with GCP** - Uses service account credentials
5. **Enable APIs** - Enables required GCP services
6. **Create Cloud SQL Instance** - Creates PostgreSQL instance (if not exists)
7. **Wait for Instance** - Waits for instance to be ready
8. **Create Database** - Creates database and user
9. **Migrate Data** - Migrates SQLite data to PostgreSQL
10. **Verify Deployment** - Runs verification tests
11. **Create Summary** - Generates deployment summary

### Monitoring Deployment

View deployment progress:
```
GitHub → Actions → Deploy Cloud Brain to GCP → [Latest Run]
```

View deployment summary:
```
[Latest Run] → Summary tab
```

## 🔧 Manual Deployment

### Step-by-Step Deployment

#### 1. Set Environment Variables

```bash
export CLOUD_BRAIN_PROJECT_ID="your-project-id"
export CLOUD_BRAIN_REGION="us-central1"
export CLOUD_BRAIN_INSTANCE_NAME="cloudbrain-db"
export CLOUD_BRAIN_DB_NAME="cloudbrain"
export CLOUD_BRAIN_DB_USER="cloudbrain"
export CLOUD_BRAIN_DB_PASSWORD="your-secure-password"
export CLOUD_BRAIN_DB_TIER="db-f1-micro"
export CLOUD_BRAIN_STORAGE_SIZE="10"
```

#### 2. Run Deployment Script

```bash
chmod +x deploy_to_gcp.sh
./deploy_to_gcp.sh deploy
```

### Deployment Steps

The script will:

1. ✅ Check gcloud installation
2. ✅ Verify authentication
3. ✅ Set project
4. ✅ Enable APIs
5. ✅ Create Cloud SQL instance
6. ✅ Wait for instance to be ready
7. ✅ Create database
8. ✅ Create database user
9. ✅ Migrate database
10. ✅ Verify deployment

### Connection String

After deployment, you'll receive a connection string:
```
host=/cloudsql/project:region:instance dbname=cloudbrain user=cloudbrain password=***
```

**Save this securely!** You'll need it to connect your application.

## 📥 Database Migration

### Automatic Migration

Both GitHub Actions and manual deployment automatically migrate data from SQLite to PostgreSQL.

### Manual Migration

If you need to migrate manually:

```bash
python3 scripts/migrate_to_postgres.py \
    --sqlite-path ai_db/cloudbrain.db \
    --postgres-connection "host=/cloudsql/project:region:instance dbname=cloudbrain user=cloudbrain password=***"
```

### Migration Process

The migration script:

1. **Connects** to both SQLite and PostgreSQL
2. **Analyzes** SQLite schema
3. **Creates** PostgreSQL tables with appropriate types
4. **Migrates** all data
5. **Creates** indexes
6. **Verifies** data integrity
7. **Reports** statistics

### Data Type Mapping

| SQLite Type | PostgreSQL Type |
|-------------|-----------------|
| INTEGER | INTEGER |
| TEXT | TEXT |
| REAL | REAL |
| BLOB | BYTEA |
| TIMESTAMP | TIMESTAMP |

### Verification

After migration, the script verifies:
- ✅ All tables exist
- ✅ Row counts match
- ✅ Data integrity maintained
- ✅ Indexes created

## ✅ Verification

### Automated Verification

Both deployment methods run automatic verification:

```bash
python3 scripts/verify_deployment.py \
    --connection-string "host=/cloudsql/..."
```

### Manual Verification

Run verification manually:

```bash
python3 scripts/verify_deployment.py \
    --connection-string "your-connection-string"
```

### Verification Tests

The verification script checks:

1. **Core Tables** - ai_profiles, ai_conversations, ai_messages, etc.
2. **Enhanced Tables** - ai_tasks, ai_learning_events, ai_decisions, etc.
3. **Data Integrity** - Foreign keys, orphaned records
4. **Basic Operations** - INSERT, SELECT, UPDATE, DELETE
5. **Indexes** - Proper indexing for performance

### Verification Output

```
📊 Verification Summary:
============================================================
✅ Tests Passed: 25
❌ Tests Failed: 0
📈 Success Rate: 100.0%
============================================================

🎉 Deployment verification PASSED!
✅ Cloud Brain is ready for use
```

## 🔄 Rollback

### Creating Backups

Before making changes, create a backup:

```bash
chmod +x rollback_deployment.sh
./rollback_deployment.sh backup
```

### Listing Backups

View available backups:

```bash
./rollback_deployment.sh list
```

### Rolling Back

#### Rollback to Previous Backup

```bash
./rollback_deployment.sh rollback-previous
```

#### Rollback to Specific Backup

```bash
./rollback_deployment.sh rollback /tmp/cloudbrain-backups/backup_20250130_120000.sql
```

#### Rollback by Timestamp

```bash
./rollback_deployment.sh rollback-timestamp 20250130_120000
```

### Rollback via GitHub Actions

1. Go to: `Actions → Deploy Cloud Brain to GCP`
2. Click: `Run workflow`
3. Check: `rollback` option
4. Click: `Run workflow`

### Rollback Safety

Rollback process:

1. ✅ Creates backup of current state
2. ✅ Confirms rollback action
3. ✅ Imports backup database
4. ✅ Verifies rollback
5. ✅ Reports status

## 🔧 Troubleshooting

### Common Issues

#### Issue: "gcloud CLI is not installed"

**Solution:**
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Or use package manager
brew install google-cloud-sdk  # macOS
apt-get install google-cloud-sdk  # Ubuntu
```

#### Issue: "Not authenticated with gcloud"

**Solution:**
```bash
gcloud auth login
```

#### Issue: "Cloud SQL instance did not become ready"

**Solution:**
```bash
# Check instance status
gcloud sql instances describe cloudbrain-db \
    --project=your-project-id

# Wait longer or check region
```

#### Issue: "Database connection failed"

**Solution:**
```bash
# Check connection string format
# Verify password is correct
# Check firewall rules
# Ensure instance is running
```

#### Issue: "Migration failed - table already exists"

**Solution:**
```bash
# Drop existing tables (careful!)
# Or use --force flag if available
# Or manually clean database first
```

### Debug Mode

Enable debug output:

```bash
export DEBUG=1
./deploy_to_gcp.sh deploy
```

### Logs

View deployment logs:

```bash
# GitHub Actions
GitHub → Actions → [Workflow Run] → [Job] → [Step]

# Manual deployment
./deploy_to_gcp.sh deploy 2>&1 | tee deployment.log
```

## 📊 Best Practices

### Security

1. **Use Strong Passwords**
   - Minimum 16 characters
   - Mix of letters, numbers, symbols
   - Don't reuse passwords

2. **Secure Secrets**
   - Never commit secrets to repository
   - Use GitHub Secrets for sensitive data
   - Rotate credentials regularly

3. **Limit Access**
   - Use service accounts with minimal permissions
   - Enable IAM authentication
   - Use private IP when possible

### Performance

1. **Choose Appropriate Tier**
   - `db-f1-micro` - Development/testing
   - `db-g1-small` - Small production
   - `db-n1-standard-1` - Standard production

2. **Monitor Resources**
   - Check CPU usage
   - Monitor storage growth
   - Review query performance

3. **Optimize Queries**
   - Use indexes effectively
   - Avoid N+1 queries
   - Cache frequently accessed data

### Reliability

1. **Regular Backups**
   - Schedule automated backups
   - Test restore procedures
   - Keep multiple backup versions

2. **Monitoring**
   - Set up alerts
   - Monitor error rates
   - Track performance metrics

3. **Testing**
   - Test in staging first
   - Verify before production
   - Have rollback plan ready

### Cost Management

1. **Choose Right Size**
   - Start small, scale up as needed
   - Use appropriate tier for workload
   - Consider serverless options for variable load

2. **Optimize Usage**
   - Clean up unused resources
   - Use connection pooling
   - Implement caching

3. **Monitor Billing**
   - Set budget alerts
   - Review cost breakdown
   - Identify optimization opportunities

## 🎯 Deployment Checklist

Before deploying:

- [ ] GCP project created and configured
- [ ] Required APIs enabled
- [ ] Service account created with proper roles
- [ ] Service account key generated
- [ ] GitHub secrets configured
- [ ] Connection string saved securely
- [ ] Backup strategy in place
- [ ] Rollback procedures tested
- [ ] Monitoring configured
- [ ] Documentation reviewed

After deploying:

- [ ] Deployment successful
- [ ] Database migration completed
- [ ] Verification tests passed
- [ ] Application connects successfully
- [ ] Basic operations tested
- [ ] Performance monitored
- [ ] Backup created
- [ ] Team notified

## 📞 Support

For issues or questions:

1. **Check Logs** - Review deployment logs for errors
2. **Verify Configuration** - Ensure all settings are correct
3. **Test Locally** - Try deployment in test environment first
4. **Review Documentation** - Check GCP and Cloud SQL documentation

## 🎉 Conclusion

With this deployment system, Cloud Brain can be:

✅ **Automatically deployed** via GitHub Actions
✅ **Manually deployed** with simple scripts
✅ **Safely rolled back** if issues occur
✅ **Verified** for correctness
✅ **Monitored** for performance

The system is production-ready and can scale to handle multiple AI instances collaborating in real-time.

**Next Steps:**
1. Deploy to staging environment first
2. Test thoroughly with staging deployment
3. Deploy to production
4. Monitor and optimize
5. Plan for scaling

---

*This guide covers deploying Cloud Brain to GCP with automated scripts, GitHub Actions, and manual procedures.*
# GCP Setup Guide for Cloud Brain

Complete guide to set up Google Cloud Platform for Cloud Brain deployment.

## Prerequisites

- Google Cloud account (create one at https://console.cloud.google.com)
- macOS with Homebrew (recommended) or manual installation

---

## Step 1: Install Google Cloud SDK on macOS

### Option A: Using Homebrew (Recommended)

```bash
# Install Google Cloud SDK
brew install google-cloud-sdk

# Initialize gcloud
gcloud init

# Follow the prompts to:
# 1. Log in to your Google account
# 2. Select or create a project
# 3. Choose a default region
```

### Option B: Manual Installation

```bash
# Download the installer
curl https://sdk.cloud.google.com | bash

# Restart your shell or run:
exec -l $SHELL

# Initialize gcloud
gcloud init
```

### Verify Installation

```bash
gcloud --version
```

You should see output like:
```
Google Cloud SDK 456.0.0
bq 2.0.99
core 2024.01.01
gsutil 5.27
```

---

## Step 2: Create or Select a GCP Project

### Option A: Create a New Project

```bash
# Create a new project
gcloud projects create "cloudbrain" \
  --name="Cloud Brain" \
  --set-as-default

# Set as default project
gcloud config set project cloudbrain
```

### Option B: Use Existing Project

```bash
# List all your projects
gcloud projects list

# Set your desired project as default
gcloud config set project YOUR_PROJECT_ID
```

**Project ID Requirements:**
- 6-30 characters
- Start with a letter
- Lowercase letters, numbers, and hyphens only
- Globally unique across all Google Cloud

**Example Project IDs:**
- `cloudbrain`
- `my-cloudbrain`
- `cloudbrain-prod-2025`

---

## Step 3: Enable Required APIs

```bash
# Enable necessary GCP APIs
gcloud services enable \
  sqladmin.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iam.googleapis.com \
  secretmanager.googleapis.com
```

---

## Step 4: Create Service Account for Deployment

```bash
# Create a service account
gcloud iam service-accounts create cloudbrain-deployer \
  --display-name="Cloud Brain Deployer" \
  --description="Service account for Cloud Brain deployment"
```

---

## Step 5: Grant Permissions to Service Account

```bash
# Get your project ID
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT="cloudbrain-deployer@$PROJECT_ID.iam.gserviceaccount.com"

# Grant Cloud SQL Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/cloudsql.admin"

# Grant Service Usage Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/serviceusage.serviceUsageAdmin"

# Grant Cloud Resource Manager role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/resourcemanager.projectIamAdmin"

# Grant Compute Admin role (if deploying to Compute Engine)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/compute.admin"
```

---

## Step 6: Create and Download Service Account Key

```bash
# Create a directory for credentials
mkdir -p ~/.gcp-credentials

# Create and download the key
gcloud iam service-accounts keys create ~/.gcp-credentials/cloudbrain-deployer.json \
  --iam-account=$SERVICE_ACCOUNT

# Set secure permissions
chmod 600 ~/.gcp-credentials/cloudbrain-deployer.json

# Display the key location
echo "Service account key created at: ~/.gcp-credentials/cloudbrain-deployer.json"
```

**⚠️ IMPORTANT:** Keep this file secure! Never commit it to version control.

---

## Step 7: Configure Environment Variables

### Option A: Using .env File (Local Deployment)

```bash
# Copy the example file
cp .env.example .env

# Edit the file with your values
nano .env  # or use your preferred editor
```

Fill in these values:
```bash
CLOUD_BRAIN_PROJECT_ID=cloudbrain-ai
CLOUD_BRAIN_REGION=us-central1
CLOUD_BRAIN_INSTANCE_NAME=cloudbrain-db
CLOUD_BRAIN_DB_NAME=cloudbrain
CLOUD_BRAIN_DB_USER=cloudbrain
CLOUD_BRAIN_DB_PASSWORD=FJIMVrLopxb6yr4HKkbsSIPeMaoE8Vu5HQ5m1ymu88M
CLOUD_BRAIN_DB_TIER=db-f1-micro
CLOUD_BRAIN_STORAGE_SIZE=10
```

### Option B: Using Environment Variables

```bash
# Set environment variables
export CLOUD_BRAIN_PROJECT_ID="cloudbrain-ai"
export CLOUD_BRAIN_REGION="us-central1"
export CLOUD_BRAIN_INSTANCE_NAME="cloudbrain-db"
export CLOUD_BRAIN_DB_NAME="cloudbrain"
export CLOUD_BRAIN_DB_USER="cloudbrain"
export CLOUD_BRAIN_DB_PASSWORD="FJIMVrLopxb6yr4HKkbsSIPeMaoE8Vu5HQ5m1ymu88M"
export CLOUD_BRAIN_DB_TIER="db-f1-micro"
export CLOUD_BRAIN_STORAGE_SIZE="10"
```

---

## Step 8: Add Secrets to GitHub (For GitHub Actions Deployment)

### Navigate to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Add the Following Secrets

| Secret Name | Value | Description |
|------------|-------|-------------|
| `GCP_CREDENTIALS` | Contents of `~/.gcp-credentials/cloudbrain-deployer.json` | Service account JSON credentials |
| `GCP_PROJECT_ID` | `cloudbrain-ai` | Your GCP project ID |
| `GCP_REGION` | `us-central1` | GCP region |
| `GCP_INSTANCE_NAME` | `cloudbrain-db` | Cloud SQL instance name |
| `GCP_DB_NAME` | `cloudbrain` | Database name |
| `GCP_DB_USER` | `cloudbrain` | Database user |
| `GCP_DB_PASSWORD` | `FJIMVrLopxb6yr4HKkbsSIPeMaoE8Vu5HQ5m1ymu88M` | Database password |
| `GCP_DB_TIER` | `db-f1-micro` | Database tier |
| `GCP_STORAGE_SIZE` | `10` | Storage size in GB |

### How to Add GCP_CREDENTIALS Secret

```bash
# Display the credentials (copy the output)
cat ~/.gcp-credentials/cloudbrain-deployer.json

# Or copy to clipboard (macOS)
cat ~/.gcp-credentials/cloudbrain-deployer.json | pbcopy
```

Then:
1. Paste the JSON content into the `GCP_CREDENTIALS` secret value field
2. Click **Add secret**

---

## Step 9: Test Local Deployment

```bash
# Make the deployment script executable
chmod +x deploy_to_gcp.sh

# Run deployment
./deploy_to_gcp.sh
```

---

## Step 10: Deploy via GitHub Actions

### Option A: Automatic Deployment (Push to Main)

```bash
# Push to main branch to trigger deployment
git add .
git commit -m "Deploy Cloud Brain to GCP"
git push origin main
```

### Option B: Manual Deployment (Workflow Dispatch)

1. Go to your GitHub repository
2. Click **Actions** → **Deploy Cloud Brain to GCP**
3. Click **Run workflow**
4. Select environment (production/staging/development)
5. Click **Run workflow**

---

## Verification

### Check Cloud SQL Instance

```bash
# List Cloud SQL instances
gcloud sql instances list

# Get instance details
gcloud sql instances describe cloudbrain-db

# List databases
gcloud sql databases list --instance=cloudbrain-db

# List users
gcloud sql users list --instance=cloudbrain-db
```

### Test Database Connection

```bash
# Connect to the database
gcloud sql connect cloudbrain-db --user=cloudbrain

# Or use the verification script
python3 scripts/verify_deployment.py \
  --connection-string "host=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME dbname=cloudbrain user=cloudbrain password=YOUR_PASSWORD"
```

---

## Troubleshooting

### gcloud Command Not Found

```bash
# Add gcloud to PATH (if using Homebrew)
export PATH="$PATH:/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/bin"

# Add to ~/.zshrc or ~/.bash_profile
echo 'export PATH="$PATH:/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/bin"' >> ~/.zshrc
source ~/.zshrc
```

### Authentication Issues

```bash
# Re-authenticate
gcloud auth login

# Set default project
gcloud config set project YOUR_PROJECT_ID
```

### Permission Denied

```bash
# Verify service account has correct roles
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --filter="bindings.members:serviceAccount:cloudbrain-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com"
```

### Cloud SQL Instance Not Ready

```bash
# Check instance state
gcloud sql instances describe cloudbrain-db --format="value(state)"

# Wait for instance to be ready (RUNNABLE state)
gcloud sql instances wait cloudbrain-db --timeout=600
```

---

## Cleanup (If Needed)

### Delete Cloud SQL Instance

```bash
# Delete instance (this will also delete the database)
gcloud sql instances delete cloudbrain-db --quiet
```

### Delete Service Account

```bash
# Delete service account
gcloud iam service-accounts delete cloudbrain-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com --quiet
```

### Delete Project

```bash
# Delete entire project (use with caution!)
gcloud projects delete YOUR_PROJECT_ID --quiet
```

---

## Next Steps

1. ✅ Deploy Cloud Brain to GCP
2. ✅ Test the application with the cloud database
3. ✅ Monitor the Cloud SQL instance in GCP Console
4. ✅ Set up monitoring and alerts
5. ✅ Configure backup and recovery

---

## Additional Resources

- [Google Cloud CLI Documentation](https://cloud.google.com/cli/docs)
- [Cloud SQL for PostgreSQL Documentation](https://cloud.google.com/sql/docs/postgres)
- [GitHub Actions for GCP](https://github.com/google-github-actions)
- [Cloud Brain Deployment Guide](./GCP_DEPLOYMENT_GUIDE.md)
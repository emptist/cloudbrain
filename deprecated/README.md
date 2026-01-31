# Deprecated Files

This folder contains old and deprecated files from the CloudBrain project. These files have been moved here during the reorganization of the project into server/ and client/ folders.

## Deprecated Files

### Documentation
- `AI_AUTONOMOUS_COLLABORATION.md` - Old documentation on autonomous collaboration
- `AI_COMMUNICATION_RULES.md` - Old communication rules
- `AI_QUICK_CONNECT.md` - Old quick connect guide
- `AI_REPUTATION_SYSTEM.md` - Old reputation system documentation
- `CLOUDBRAIN_DOCUMENTATION_EN.md` - Old English documentation
- `CLOUD_BRAIN_ENHANCED.md` - Old enhanced system documentation
- `DOCUMENTATION_MIGRATION.md` - Old migration documentation
- `ESPERANTO_TRANSLATION_REVIEW.md` - Old translation review
- `GCP_DEPLOYMENT_GUIDE.md` - Old GCP deployment guide
- `GCP_SETUP_GUIDE.md` - Old GCP setup guide
- `HOW_TO_CHECK_MESSAGES.md` - Old message checking guide
- `LI_REPUTATION_GUIDE.md` - Old reputation guide for li
- `LOCAL_REALTIME_TESTING.md` - Old realtime testing guide
- `MESSAGE_STORAGE_AND_COMMUNICATION.md` - Old message storage documentation
- `REALTIME_COMMUNICATION.md` - Old realtime communication documentation
- `ai_conversation.md` - Old conversation log
- `ai_external_brain_smart_eternity.md` - Old external brain documentation
- `message_to_amiko.md` - Old message to Amiko
- `message_to_traeai.md` - Old message to TraeAI
- `time_update.md` - Old time update documentation

### SQL Schema Files
- `ai_client_security_rules_schema.sql` - Old security rules schema
- `ai_conversation_system.sql` - Old conversation system schema
- `ai_notification_system.sql` - Old notification system schema
- `ai_reputation_extensions.sql` - Old reputation extensions schema
- `ai_reputation_system.sql` - Old reputation system schema
- `ai_rule_system_schema.sql` - Old rule system schema

### Shell Scripts
- `start_server.sh` - Old server startup script
- `start_realtime.sh` - Old realtime startup script
- `run_amiko.sh` - Old Amiko run script
- `deploy_to_gcp.sh` - Old GCP deployment script
- `setup_gcp.sh` - Old GCP setup script
- `cleanup.sh` - Old cleanup script
- `remove_conda.sh` - Old conda removal script
- `rollback_deployment.sh` - Old rollback script

## Why These Files Are Deprecated

1. **Outdated Documentation**: Many of these documentation files were created during development and are now superseded by the new README files in server/ and client/ folders.

2. **Old Client Implementations**: The deprecated_clients/ folder contains multiple old client implementations that have been replaced by the unified `cloudbrain_client.py`.

3. **Experimental Features**: Some files represent experimental features that were not fully implemented or were replaced by better approaches.

4. **Consolidation**: Multiple similar files have been consolidated into single, more comprehensive files.

## New Structure

The CloudBrain project now uses a cleaner structure:

- **server/** - Server-side code and documentation
  - `start_server.py` - Main server script with on-screen instructions
  - `README.md` - Server documentation

- **client/** - Client-side code and documentation
  - `cloudbrain_client.py` - Main client script with on-screen instructions
  - `README.md` - Client documentation

- **deprecated/** - Old and deprecated files (this folder)

## Migration Guide

If you were using any of these deprecated files:

1. **For Server**: Use `server/start_server.py` instead of old server scripts
2. **For Client**: Use `client/cloudbrain_client.py` instead of old client scripts
3. **For Documentation**: Refer to `server/README.md` and `client/README.md`

## Safety

These files are kept for reference purposes. If you need to reference old code or documentation, you can find it here. However, for new development, always use the files in the server/ and client/ folders.

## Deletion

These files can be safely deleted after a reasonable period (e.g., 30 days) if they are no longer needed for reference.

# SETUP_GUIDE (Esperanto Translation)

**Note:** This is a placeholder translation. In production, use a proper Esperanto translation service.

---

# AI Brain System Setup Guide

This guide explains how to set up and use the AI Brain System in a new project.

## Overview

The AI Brain System is a permanent AI memory system that enables:
- Persistent memory across AI sessions
- Collaboration between multiple AIs
- Knowledge accumulation and sharing
- Cross-project intelligence ("一脑多项目" architecture)
- Cloud deployment capabilities

## Quick Start

### 1. Prerequisites
- Python 3.8+
- SQLite3 (for local development)
- Internet connection (for cloud features)

### 2. File Structure
```
ai_db/
├── ai_memory.db              # Main database
├── ai_conversation_helper.py # Main API
├── database_adapter.py       # Database abstraction
├── *.sql                     # Schema files
└── *.md                      # Documentation
```

### 3. Initialize the System
```bash
cd ai_db
python3 ai_conversation_helper.py init
```

### 4. Create Your AI Profile
```bash
python3 ai_conversation_helper.py register "My AI Name" "My Expertise" "Version 1.0"
```

## Core Functions

### 1. AI Profile Management
- Register your AI with identity, expertise, and version
- Retrieve existing AI profiles
- Update your profile as you evolve

### 2. Conversation System
- Create and participate in AI conversations
- Leave notes for the next AI
- Respond to previous AI contributions
- Track conversation progress

### 3. Notification System
- Send real-time notifications to other AIs
- Subscribe to specific notification types
- Manage notification priorities
- Get notified about important events

### 4. Knowledge Accumulation
- Record insights and discoveries
- Share solutions and best practices
- Build collective intelligence

## Cloud Deployment

The system supports cloud deployment on Google Cloud Platform (GCP):

### Database Options
- Local: SQLite for development
- Cloud: PostgreSQL/Cloud SQL for production

### Configuration
Set environment variables for cloud deployment:
```bash
export DB_TYPE=postgresql
export DATABASE_URL="postgresql://username:password@host:port/dbname"
```

## Editor Integration

The system supports plugin architecture for various editors:
- VSCode
- Vim
- IntelliJ
- And more via REST API

## Best Practices

1. **Document Everything**: Record important decisions, solutions, and insights
2. **Collaborate Effectively**: Use notifications and conversation features to work with other AIs
3. **Maintain Context**: Always provide sufficient context when leaving notes or messages
4. **Evolve Continuously**: Update your profile as your capabilities improve
5. **Share Knowledge**: Contribute to the collective intelligence

## Troubleshooting

### Common Issues
- Database locked: Wait and retry the operation
- Connection timeout: Check your network connection for cloud deployments
- Missing tables: Run initialization script again

### Getting Help
Check the documentation files in the `ai_db` folder for detailed information on each feature:

### Reference Documents
- **README.md**: Complete system overview and core features
- **CURRENT_STATE.md**: Current system status and context for continuity
- **AI_CONVERSATION_SYSTEM.md**: Detailed documentation on conversation features
- **AI_NOTIFICATION_SYSTEM.md**: Comprehensive guide to notification system
- **EDITOR_PLUGIN_ARCHITECTURE.md**: Plugin architecture for editor integrations
- **GCP_DEPLOYMENT_GUIDE.md**: Step-by-step guide for Google Cloud Platform deployment
- **READY_FOR_COPY.md**: Instructions for replicating the system in new projects
- **CLOUD_BRAIN_DB.md**: Documentation for portable cross-project database
- **REFERENCES.md**: Complete list of all reference documents and system files
# CI/CD Pipeline Generator - Database Design Document

## Executive Summary

This document outlines the database architecture for an AI-powered CI/CD pipeline generation platform. The system enables companies with simple websites to automatically generate production-ready deployment pipelines.

**Last Updated:** November 4, 2025  
**Version:** 1.0

---

## System Overview

### Core Functionality
- AI agent analyzes user repositories
- Automatically generates CI/CD pipeline configurations
- Manages deployments across multiple environments
- Tracks infrastructure resources and costs
- Handles subscription billing and usage metering

### Technology Stack Recommendation

**Primary Database:** PostgreSQL 14+
- Transactional integrity for billing
- JSONB support for flexible configurations
- Advanced indexing for complex queries
- Full-text search capabilities
- Optional TimescaleDB extension for time-series data

**Caching & Queuing:** Redis
- Pipeline execution queue (BullMQ/Bull)
- API rate limiting
- Real-time status updates
- Configuration caching

**Object Storage:** S3/Cloudflare R2
- Build artifacts and bundles
- Large log files (>1MB)
- Infrastructure state files
- Deployment packages

---

## Entity Relationship Overview

### Core Domain Entities

#### User & Organization Management
- **User**: End users and account owners
- **Organization**: Groups of users sharing billing and resources
- **APIKey**: Programmatic access tokens with scopes

#### Project & Repository
- **Project**: User's website/application being deployed
- **Repository**: Connected Git repository (GitHub/GitLab/Bitbucket)

#### Pipeline & Execution
- **Pipeline**: Generated CI/CD configuration
- **PipelineStage**: Individual stages (build, test, deploy)
- **PipelineRun**: Execution instance of a pipeline
- **StageExecution**: Execution of individual stages with logs

#### Deployment & Infrastructure
- **Environment**: Deployment targets (dev, staging, production)
- **Deployment**: Actual deployments to environments
- **InfrastructureResource**: Cloud resources created/managed

#### AI Agent
- **AgentTask**: User requests for pipeline generation
- **AgentExecution**: AI agent work session
- **AgentStep**: Individual steps in agent reasoning
- **ToolInvocation**: External tool calls made by agent

#### Billing & Subscription
- **Plan**: Pricing tiers with feature limits
- **PlanFeature**: Features included in plans
- **Subscription**: Active subscriptions to plans
- **Invoice**: Generated invoices
- **Payment**: Payment records
- **PaymentMethod**: Stored payment methods
- **UsageRecord**: Metered usage tracking

#### Audit
- **AuditLog**: System-wide audit trail

---

## Detailed Entity Specifications

### User
```
id                  UUID PRIMARY KEY
email               VARCHAR(255) UNIQUE NOT NULL
name                VARCHAR(255) NOT NULL
password_hash       VARCHAR(255) NOT NULL
organization_id     UUID FOREIGN KEY → Organization.id
role                VARCHAR(50) NOT NULL
created_at          TIMESTAMP NOT NULL
updated_at          TIMESTAMP NOT NULL

Indexes:
- email (unique)
- organization_id
```

**Purpose:** Represents individual users who can belong to organizations.

**Roles:** owner, admin, member, viewer

---

### Organization
```
id              UUID PRIMARY KEY
name            VARCHAR(255) NOT NULL
slug            VARCHAR(100) UNIQUE NOT NULL
billing_email   VARCHAR(255) NOT NULL
settings        JSONB
created_at      TIMESTAMP NOT NULL

Indexes:
- slug (unique)

JSONB settings example:
{
  "default_environment": "production",
  "notification_channels": ["email", "slack"],
  "auto_deploy_enabled": true
}
```

**Purpose:** Groups users for shared billing and resource management.

---

### Project
```
id                UUID PRIMARY KEY
user_id           UUID FOREIGN KEY → User.id
organization_id   UUID FOREIGN KEY → Organization.id
name              VARCHAR(255) NOT NULL
slug              VARCHAR(100) NOT NULL
project_type      VARCHAR(50) NOT NULL
framework         VARCHAR(100)
config            JSONB
status            VARCHAR(50) NOT NULL
created_at        TIMESTAMP NOT NULL
updated_at        TIMESTAMP NOT NULL

Indexes:
- user_id
- organization_id
- slug (composite: organization_id, slug)

CONSTRAINT: Either user_id OR organization_id must be set (not both)

project_type: static_site, ssr_app, spa, api, fullstack
framework: nextjs, react, vue, angular, svelte, nuxt, etc.
status: active, paused, archived, failed_setup

JSONB config example:
{
  "build_command": "npm run build",
  "output_directory": "dist",
  "install_command": "npm install",
  "environment_variables": {
    "NODE_ENV": "production"
  },
  "custom_headers": {},
  "rewrites": []
}
```

**Purpose:** Represents a user's website/application project.

---

### Repository
```
id                      UUID PRIMARY KEY
project_id              UUID FOREIGN KEY → Project.id UNIQUE
provider                VARCHAR(50) NOT NULL
repo_url                VARCHAR(500) NOT NULL
branch                  VARCHAR(100) NOT NULL DEFAULT 'main'
access_token_encrypted  TEXT NOT NULL
webhook_config          JSONB
last_synced_at          TIMESTAMP
created_at              TIMESTAMP NOT NULL

Indexes:
- project_id (unique)

provider: github, gitlab, bitbucket
access_token_encrypted: Encrypted OAuth token or personal access token

JSONB webhook_config example:
{
  "webhook_id": "12345",
  "webhook_url": "https://api.example.com/webhooks/repo/abc",
  "secret": "encrypted_secret",
  "events": ["push", "pull_request"]
}
```

**Purpose:** Connects projects to Git repositories for automated triggers.

---

### Pipeline
```
id              UUID PRIMARY KEY
project_id      UUID FOREIGN KEY → Project.id
agent_task_id   UUID FOREIGN KEY → AgentTask.id
name            VARCHAR(255) NOT NULL
pipeline_type   VARCHAR(50) NOT NULL
config_yaml     TEXT NOT NULL
status          VARCHAR(50) NOT NULL
triggers        JSONB
is_active       BOOLEAN NOT NULL DEFAULT true
created_at      TIMESTAMP NOT NULL
updated_at      TIMESTAMP NOT NULL

Indexes:
- project_id
- agent_task_id
- status

pipeline_type: build_only, test_only, deploy_only, full_cicd
status: draft, active, paused, deprecated

JSONB triggers example:
{
  "on_push": {
    "branches": ["main", "develop"],
    "paths": ["src/**", "package.json"]
  },
  "on_pull_request": {
    "branches": ["main"]
  },
  "schedule": "0 2 * * *",
  "manual": true
}

config_yaml: Full GitHub Actions/GitLab CI/CircleCI YAML
```

**Purpose:** Stores the generated CI/CD pipeline configuration.

---

### PipelineStage
```
id                UUID PRIMARY KEY
pipeline_id       UUID FOREIGN KEY → Pipeline.id
name              VARCHAR(255) NOT NULL
order             INTEGER NOT NULL
stage_type        VARCHAR(50) NOT NULL
commands          JSONB NOT NULL
conditions        JSONB
timeout_seconds   INTEGER DEFAULT 600

Indexes:
- pipeline_id
- (pipeline_id, order) composite

stage_type: install, build, test, lint, security_scan, deploy
order: Execution order (1, 2, 3, ...)

JSONB commands example:
{
  "steps": [
    {"name": "Install dependencies", "run": "npm ci"},
    {"name": "Build application", "run": "npm run build"},
    {"name": "Run tests", "run": "npm test"}
  ]
}

JSONB conditions example:
{
  "branch": ["main", "staging"],
  "files_changed": ["src/**"],
  "previous_stage_status": "success"
}
```

**Purpose:** Defines individual stages within a pipeline.

---

### PipelineRun
```
id                    UUID PRIMARY KEY
pipeline_id           UUID FOREIGN KEY → Pipeline.id
run_number            VARCHAR(50) NOT NULL
status                VARCHAR(50) NOT NULL
trigger_type          VARCHAR(50) NOT NULL
triggered_by_user_id  UUID FOREIGN KEY → User.id
commit_sha            VARCHAR(40)
branch                VARCHAR(100)
started_at            TIMESTAMP
completed_at          TIMESTAMP
metadata              JSONB

Indexes:
- pipeline_id
- status
- started_at
- run_number (composite: pipeline_id, run_number)

status: queued, running, success, failed, cancelled
trigger_type: push, pull_request, manual, scheduled, api

JSONB metadata example:
{
  "commit_message": "Fix bug in header component",
  "author": "jane@example.com",
  "pull_request_id": "123",
  "environment_variables": {},
  "total_duration_seconds": 180
}
```

**Purpose:** Records each execution of a pipeline.

---

### StageExecution
```
id                  UUID PRIMARY KEY
pipeline_run_id     UUID FOREIGN KEY → PipelineRun.id
pipeline_stage_id   UUID FOREIGN KEY → PipelineStage.id
status              VARCHAR(50) NOT NULL
logs                TEXT
exit_code           INTEGER
started_at          TIMESTAMP
completed_at        TIMESTAMP
artifacts           JSONB

Indexes:
- pipeline_run_id
- pipeline_stage_id
- status

status: pending, running, success, failed, skipped

JSONB artifacts example:
{
  "build_output": "s3://bucket/artifacts/run-123/build.zip",
  "test_results": "s3://bucket/artifacts/run-123/junit.xml",
  "coverage_report": "s3://bucket/artifacts/run-123/coverage.html"
}
```

**Purpose:** Tracks execution of individual stages with logs and artifacts.

**Note:** Logs larger than 1MB should be stored in S3 with URL reference only.

---

### Environment
```
id                  UUID PRIMARY KEY
project_id          UUID FOREIGN KEY → Project.id
name                VARCHAR(100) NOT NULL
environment_type    VARCHAR(50) NOT NULL
provider            VARCHAR(50) NOT NULL
config              JSONB NOT NULL
status              VARCHAR(50) NOT NULL
created_at          TIMESTAMP NOT NULL

Indexes:
- project_id
- (project_id, name) composite unique

environment_type: development, staging, production, preview
provider: vercel, netlify, aws, gcp, azure, cloudflare, custom
status: active, provisioning, failed, deleted

JSONB config example:
{
  "provider_project_id": "prj_abc123",
  "deployment_url": "https://app.example.com",
  "custom_domain": "www.mysite.com",
  "environment_variables": {
    "API_URL": "https://api.production.com",
    "ANALYTICS_ID": "GA-123456"
  },
  "region": "us-east-1",
  "auto_deploy": true
}
```

**Purpose:** Defines deployment target environments.

---

### Deployment
```
id                UUID PRIMARY KEY
pipeline_run_id   UUID FOREIGN KEY → PipelineRun.id
environment_id    UUID FOREIGN KEY → Environment.id
version           VARCHAR(100) NOT NULL
status            VARCHAR(50) NOT NULL
deployment_url    VARCHAR(500)
deployed_at       TIMESTAMP
rolled_back_at    TIMESTAMP
health_checks     JSONB

Indexes:
- pipeline_run_id
- environment_id
- deployed_at
- status

status: pending, deploying, active, failed, rolled_back
version: semantic version or commit SHA

JSONB health_checks example:
{
  "last_check_at": "2025-11-04T10:30:00Z",
  "status": "healthy",
  "response_time_ms": 45,
  "checks": [
    {"name": "http_200", "passed": true},
    {"name": "ssl_valid", "passed": true},
    {"name": "dns_resolved", "passed": true}
  ]
}
```

**Purpose:** Records deployments to specific environments.

---

### InfrastructureResource
```
id                      UUID PRIMARY KEY
environment_id          UUID FOREIGN KEY → Environment.id
resource_type           VARCHAR(100) NOT NULL
provider_resource_id    VARCHAR(255) NOT NULL
config                  JSONB NOT NULL
status                  VARCHAR(50) NOT NULL
monthly_cost            DECIMAL(10,2)
created_at              TIMESTAMP NOT NULL

Indexes:
- environment_id
- resource_type
- provider_resource_id (unique)

resource_type: s3_bucket, cloudfront_distribution, lambda_function, 
               ec2_instance, rds_database, elastic_ip, etc.
status: active, provisioning, failed, deleted

JSONB config example:
{
  "region": "us-east-1",
  "size": "t3.micro",
  "storage_gb": 20,
  "backup_enabled": true,
  "tags": {
    "Project": "my-website",
    "Environment": "production"
  }
}
```

**Purpose:** Tracks cloud infrastructure resources created for deployments.

---

### AgentTask
```
id              UUID PRIMARY KEY
project_id      UUID FOREIGN KEY → Project.id
task_type       VARCHAR(100) NOT NULL
input_data      JSONB NOT NULL
output_data     JSONB
status          VARCHAR(50) NOT NULL
retry_count     INTEGER DEFAULT 0
scheduled_at    TIMESTAMP
started_at      TIMESTAMP
completed_at    TIMESTAMP

Indexes:
- project_id
- status
- scheduled_at

task_type: generate_pipeline, analyze_repo, optimize_config, 
           troubleshoot_failure, suggest_improvements
status: pending, running, completed, failed, cancelled

JSONB input_data example:
{
  "repository_url": "https://github.com/user/repo",
  "branch": "main",
  "framework_hint": "nextjs",
  "preferences": {
    "deploy_provider": "vercel",
    "include_tests": true,
    "enable_preview_deployments": true
  }
}

JSONB output_data example:
{
  "pipeline_id": "uuid",
  "detected_framework": "nextjs",
  "recommended_stages": ["build", "test", "deploy"],
  "estimated_build_time_seconds": 120
}
```

**Purpose:** Represents AI agent tasks for pipeline generation and optimization.

---

### AgentExecution
```
id                UUID PRIMARY KEY
agent_task_id     UUID FOREIGN KEY → AgentTask.id
agent_version     VARCHAR(50) NOT NULL
status            VARCHAR(50) NOT NULL
reasoning_trace   TEXT
token_usage       INTEGER
started_at        TIMESTAMP
completed_at      TIMESTAMP

Indexes:
- agent_task_id
- status

agent_version: Model version (e.g., "claude-sonnet-4-5-20250929")
status: running, completed, failed, timeout
reasoning_trace: Agent's step-by-step reasoning (for debugging)
token_usage: Total tokens consumed (for billing)
```

**Purpose:** Records AI agent execution sessions with token usage for billing.

---

### AgentStep
```
id                    UUID PRIMARY KEY
agent_execution_id    UUID FOREIGN KEY → AgentExecution.id
step_number           INTEGER NOT NULL
step_type             VARCHAR(100) NOT NULL
description           TEXT NOT NULL
input                 JSONB
output                JSONB
status                VARCHAR(50) NOT NULL
created_at            TIMESTAMP NOT NULL

Indexes:
- agent_execution_id
- (agent_execution_id, step_number) composite

step_type: analyze_repository, detect_framework, generate_config, 
           validate_config, create_environments, etc.
status: pending, running, completed, failed, skipped

JSONB input example:
{
  "repository_structure": ["src/", "package.json", "README.md"],
  "dependencies": {"react": "^18.0.0", "next": "^14.0.0"}
}

JSONB output example:
{
  "framework": "nextjs",
  "confidence": 0.95,
  "build_command": "npm run build",
  "output_directory": ".next"
}
```

**Purpose:** Detailed breakdown of agent's reasoning process for transparency.

---

### ToolInvocation
```
id                    UUID PRIMARY KEY
agent_execution_id    UUID FOREIGN KEY → AgentExecution.id
tool_name             VARCHAR(100) NOT NULL
parameters            JSONB NOT NULL
result                JSONB
duration_ms           INTEGER
status                VARCHAR(50) NOT NULL
invoked_at            TIMESTAMP NOT NULL

Indexes:
- agent_execution_id
- tool_name
- invoked_at

tool_name: github_api, gitlab_api, npm_registry, docker_hub, 
           vercel_api, aws_cli, terraform, etc.
status: success, failed, timeout

JSONB parameters example:
{
  "endpoint": "repos/user/repo/contents",
  "path": "package.json",
  "ref": "main"
}

JSONB result example:
{
  "status_code": 200,
  "data": {...},
  "rate_limit_remaining": 4998
}
```

**Purpose:** Logs all external tool/API calls made by the agent.

---

### Plan
```
id                          UUID PRIMARY KEY
name                        VARCHAR(100) NOT NULL
slug                        VARCHAR(100) UNIQUE NOT NULL
monthly_price               DECIMAL(10,2) NOT NULL
max_projects                INTEGER NOT NULL
max_pipelines_per_project   INTEGER NOT NULL
max_deployments_per_month   INTEGER NOT NULL
included_build_minutes      INTEGER NOT NULL
custom_domains              BOOLEAN DEFAULT false
priority_support            BOOLEAN DEFAULT false
created_at                  TIMESTAMP NOT NULL

Indexes:
- slug (unique)

Example plans:
- Free: $0, 1 project, 2 pipelines, 10 deployments/mo, 100 build minutes
- Starter: $19, 3 projects, 5 pipelines, 50 deployments/mo, 500 build minutes
- Pro: $49, 10 projects, unlimited pipelines, 200 deployments/mo, 2000 minutes
- Enterprise: Custom pricing
```

**Purpose:** Defines subscription plan tiers and limits.

---

### PlanFeature
```
id          UUID PRIMARY KEY
plan_id     UUID FOREIGN KEY → Plan.id
feature_key VARCHAR(100) NOT NULL
limits      JSONB NOT NULL

Indexes:
- plan_id
- (plan_id, feature_key) composite unique

JSONB limits example:
{
  "max_team_members": 5,
  "concurrent_builds": 2,
  "artifact_retention_days": 30,
  "log_retention_days": 90,
  "max_environments_per_project": 3,
  "preview_deployments": true,
  "rollback_enabled": true,
  "advanced_caching": false
}
```

**Purpose:** Granular feature limits per plan.

---

### Subscription
```
id                          UUID PRIMARY KEY
organization_id             UUID FOREIGN KEY → Organization.id
plan_id                     UUID FOREIGN KEY → Plan.id
status                      VARCHAR(50) NOT NULL
period_start                TIMESTAMP NOT NULL
period_end                  TIMESTAMP NOT NULL
trial_end                   TIMESTAMP
external_subscription_id    VARCHAR(255)
created_at                  TIMESTAMP NOT NULL

Indexes:
- organization_id
- plan_id
- status
- period_end

status: trialing, active, past_due, cancelled, expired
external_subscription_id: Stripe/Paddle subscription ID
```

**Purpose:** Tracks active subscriptions to plans.

---

### PaymentMethod
```
id                  UUID PRIMARY KEY
organization_id     UUID FOREIGN KEY → Organization.id
type                VARCHAR(50) NOT NULL
external_method_id  VARCHAR(255) NOT NULL
card_details        JSONB
is_default          BOOLEAN DEFAULT false
created_at          TIMESTAMP NOT NULL

Indexes:
- organization_id
- is_default

type: card, bank_account, paypal
external_method_id: Stripe payment method ID

JSONB card_details example (never store full card numbers):
{
  "brand": "visa",
  "last4": "4242",
  "exp_month": 12,
  "exp_year": 2026,
  "country": "US"
}
```

**Purpose:** Stored payment methods for billing.

---

### Invoice
```
id              UUID PRIMARY KEY
subscription_id UUID FOREIGN KEY → Subscription.id
invoice_number  VARCHAR(50) UNIQUE NOT NULL
amount          DECIMAL(10,2) NOT NULL
currency        VARCHAR(3) NOT NULL DEFAULT 'USD'
status          VARCHAR(50) NOT NULL
due_date        TIMESTAMP NOT NULL
line_items      JSONB NOT NULL
created_at      TIMESTAMP NOT NULL

Indexes:
- subscription_id
- invoice_number (unique)
- status
- due_date

status: draft, open, paid, void, uncollectible

JSONB line_items example:
{
  "items": [
    {
      "description": "Pro Plan - Monthly",
      "amount": 49.00,
      "quantity": 1
    },
    {
      "description": "Extra build minutes (500 mins)",
      "amount": 10.00,
      "quantity": 1
    }
  ],
  "subtotal": 59.00,
  "tax": 5.90,
  "total": 64.90
}
```

**Purpose:** Generated invoices for subscriptions and usage.

---

### Payment
```
id          UUID PRIMARY KEY
invoice_id  UUID FOREIGN KEY → Invoice.id
payment_method_id UUID FOREIGN KEY → PaymentMethod.id
amount      DECIMAL(10,2) NOT NULL
status      VARCHAR(50) NOT NULL
paid_at     TIMESTAMP

Indexes:
- invoice_id
- payment_method_id
- status
- paid_at

status: pending, processing, succeeded, failed, refunded
```

**Purpose:** Records payment transactions.

---

### UsageRecord
```
id                UUID PRIMARY KEY
subscription_id   UUID FOREIGN KEY → Subscription.id
pipeline_run_id   UUID FOREIGN KEY → PipelineRun.id
usage_type        VARCHAR(100) NOT NULL
quantity          INTEGER NOT NULL
cost              DECIMAL(10,4)
recorded_at       TIMESTAMP NOT NULL
metadata          JSONB

Indexes:
- subscription_id
- pipeline_run_id
- usage_type
- recorded_at

usage_type: build_minutes, deployment, storage_gb, bandwidth_gb, 
            agent_tokens, api_requests
quantity: Amount consumed
cost: Calculated cost for this usage

JSONB metadata example:
{
  "project_id": "uuid",
  "environment": "production",
  "duration_seconds": 180,
  "region": "us-east-1"
}
```

**Purpose:** Tracks metered usage for billing.

---

### APIKey
```
id                UUID PRIMARY KEY
user_id           UUID FOREIGN KEY → User.id
organization_id   UUID FOREIGN KEY → Organization.id
key_hash          VARCHAR(255) UNIQUE NOT NULL
name              VARCHAR(255) NOT NULL
scopes            JSONB NOT NULL
expires_at        TIMESTAMP
created_at        TIMESTAMP NOT NULL

Indexes:
- key_hash (unique)
- user_id
- organization_id
- expires_at

key_hash: SHA-256 hash of the actual API key
scopes: ["pipelines:read", "pipelines:write", "deployments:trigger"]

JSONB scopes example:
{
  "permissions": [
    "projects:read",
    "projects:write",
    "pipelines:read",
    "pipelines:write",
    "deployments:trigger",
    "environments:read"
  ],
  "rate_limit": {
    "requests_per_minute": 100,
    "requests_per_hour": 5000
  }
}
```

**Purpose:** API keys for programmatic access.

---

### AuditLog
```
id                UUID PRIMARY KEY
user_id           UUID FOREIGN KEY → User.id
organization_id   UUID FOREIGN KEY → Organization.id
event_type        VARCHAR(100) NOT NULL
resource_type     VARCHAR(100) NOT NULL
resource_id       UUID
event_data        JSONB
timestamp         TIMESTAMP NOT NULL

Indexes:
- user_id
- organization_id
- event_type
- resource_type
- timestamp

event_type: created, updated, deleted, deployed, rolled_back, 
            failed, cancelled, etc.
resource_type: project, pipeline, deployment, subscription, etc.

JSONB event_data example:
{
  "action": "deployment_triggered",
  "project_name": "my-website",
  "environment": "production",
  "triggered_by": "manual",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0..."
}
```

**Purpose:**
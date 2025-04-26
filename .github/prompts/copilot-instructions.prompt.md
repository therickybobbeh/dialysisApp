# Azure Deployment Guidelines for Peritoneal Dialysis Application

## Project Overview
This document provides guidelines for refactoring the Peritoneal Dialysis Application to better support Azure deployment through CI/CD from GitHub. The application consists of a Python FastAPI backend and an Angular frontend, both containerized with Docker.

## Architecture Refactoring Goals

1. Optimize container images for Azure Container Registry
2. Replace Docker-based PostgreSQL with Azure Database for PostgreSQL
3. Configure CI/CD workflows for GitHub Actions to Azure
4. Implement Azure best practices for security and reliability

## Azure Resource Requirements

### 1. Container Registry
- Use Azure Container Registry (ACR) for storing container images
- Implement proper tagging strategy (environment, version, build ID)
- Configure CI/CD to automatically build and push images

### 2. Database
- Replace local PostgreSQL container with Azure Database for PostgreSQL Flexible Server
- Implement connection pooling for better performance
- Use Managed Identity for secure connections (no credentials in code)
- Set up automatic backups and point-in-time restore
- Configure proper firewall rules (allow only application services)

### 3. Application Hosting Options

#### Option A: Azure Container Apps (Recommended)
- Deploy backend and frontend as separate Container Apps
- Configure scaling rules based on HTTP traffic
- Set up proper health probes and readiness/liveness checks
- Use managed certificates for HTTPS

<!-- #### Option B: Azure Kubernetes Service (AKS)
- Use for more complex scenarios or when requiring advanced orchestration
- Set up proper namespace isolation
- Implement horizontal pod autoscaling
- Configure persistent volumes where needed -->

## Code Refactoring Tasks

### Dockerfile Changes
1. Backend Dockerfile refactoring:
   - Move Dockerfile back to root directory OR modify build context
   - Implement multi-stage builds for smaller images
   - Use specific Python package versions
   - Remove development dependencies from production builds
   - Set proper non-root user for security

2. Frontend Dockerfile improvements:
   - Use multi-stage build for Angular application
   - Implement proper caching of node_modules
   - Optimize production build flags

### Environment Configuration
1. Replace hard-coded environment variables and .env files:
   - Use Azure Key Vault for secrets
   - Leverage App Configuration for application settings
   - Implement feature flags where applicable

2. Database configuration:
   - Update database connection string pattern to use Azure PostgreSQL
   - Implement connection pooling with retry logic
   - Add support for Managed Identity authentication

### Logging and Monitoring
1. Implement Azure Application Insights integration
   - Add application insights library to both frontend and backend
   - Configure proper operation correlation
   - Set up custom metrics for business logic

2. Configure structured logging
   - Ensure all logs are machine-parseable JSON
   - Add proper context to logs (request ID, correlation ID)
   - Set appropriate log levels

## CI/CD Pipeline Configuration

### GitHub Actions Workflow
```yaml
# Example structure for GitHub Actions workflow
name: Build and Deploy to Azure

on:
  push:
    branches: [ main, development ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      # Build and test steps
      
  deploy-to-azure:
    needs: build-and-test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      # Azure login
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
          
      # Build and push container images
      - name: Build and push container images
        uses: azure/docker-login@v1
        with:
          login-server: ${{ secrets.ACR_LOGIN_SERVER }}
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}
      
      # Deploy to Azure Container Apps or AKS
      - name: Deploy to Azure
        uses: azure/CLI@v1
        with:
          inlineScript: |
            # Deployment commands for Container Apps or AKS
```

## Security Best Practices

1. Authentication & Authorization
   - Use Azure AD for user authentication
   - Implement proper RBAC for API authorization
   - Use Managed Identities for service-to-service communication

2. Data Protection
   - Encrypt data at rest and in transit
   - Implement proper backup and recovery procedures
   - Use Azure Private Link for database connections when possible

3. Network Security
   - Configure proper network isolation
   - Use Azure Front Door or Application Gateway for edge security
   - Implement DDoS protection

## Performance Optimization

1. Caching Strategy
   - Implement Redis Cache for session data and frequent queries
   - Use CDN for static assets

2. Database Optimization
   - Review and optimize database queries
   - Implement appropriate indexing
   - Configure connection pooling with proper limits

## Immediate Action Items

1. Fix the Dockerfile issue
   - Either move back to root directory OR
   - Configure multi-stage build with proper context

2. Create Azure resources
   - Set up Azure Resource Group
   - Provision Azure Container Registry
   - Create Azure Database for PostgreSQL
   - Configure networking and security

3. Update application for Azure PostgreSQL
   - Modify connection string pattern
   - Implement retry logic for connection resilience
   - Test database migrations

4. Configure GitHub Actions workflow
   - Set up secrets in GitHub repository
   - Create service principal for Azure authentication
   - Configure build and deployment workflow

## Testing Strategy

1. Local Testing
   - Test application with Azure PostgreSQL connection
   - Validate all functionality works with remote database

2. CI/CD Testing
   - Add automated tests to CI/CD pipeline
   - Implement smoke tests after deployment
   - Add security scanning for containers

3. Production Validation
   - Monitor application insights after deployment
   - Set up alerts for critical failures
   - Implement blue/green deployment strategy
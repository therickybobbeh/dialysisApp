# Azure Deployment Instructions

This document provides detailed instructions for deploying the Peritoneal Dialysis Application to Azure using the configured CI/CD pipeline.

## Prerequisites

1. **Azure Subscription**: Active Azure subscription with contributor access
2. **GitHub Repository**: Access to the project's GitHub repository with permission to create secrets
3. **Azure CLI**: Installation of Azure CLI on your local machine (for initial setup)

## Setting Up GitHub Secrets

The CI/CD pipeline requires several secrets to be configured in your GitHub repository:

1. Navigate to your repository on GitHub
2. Go to Settings > Secrets and variables > Actions
3. Create the following secrets:

| Secret Name | Description |
|-------------|-------------|
| `AZURE_CREDENTIALS` | Service principal credentials for Azure authentication |
| `POSTGRES_ADMIN_USER` | Username for Azure PostgreSQL admin account |
| `POSTGRES_ADMIN_PASSWORD` | Password for Azure PostgreSQL admin account |
| `SECRET_KEY` | Secret key for JWT token generation |
| `REFRESH_SECRET_KEY` | Secret key for JWT refresh token generation |

## Creating Azure Service Principal

To generate the Azure credentials for GitHub Actions:

```bash
# Login to Azure
az login

# Set subscription (if you have multiple)
az account set --subscription <SUBSCRIPTION_ID>

# Create service principal with contributor role
az ad sp create-for-rbac --name "pd-management-sp" --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID> \
  --json-auth
```

Copy the entire JSON output and save it as the value for the `AZURE_CREDENTIALS` secret in GitHub.

## Deployment Options

### Option 1: Automatic Deployment

When you push to the `main` branch, the GitHub Actions workflow will automatically:
1. Build and test the application
2. Create or update Azure resources
3. Deploy both frontend and backend to Azure Container Apps

### Option 2: Manual Deployment

You can manually trigger the workflow:

1. Go to the "Actions" tab in your GitHub repository
2. Select the "Build and Deploy to Azure" workflow
3. Click "Run workflow"
4. Choose the target environment (dev or prod)
5. Click "Run workflow" to start the deployment

## Post-Deployment Steps

After successful deployment, the workflow will output the URLs for the frontend and backend applications. You should:

1. Verify the application is accessible at the provided URLs
2. Check Azure Container Apps logs for any issues
3. Monitor the application using Azure Application Insights

## Monitoring and Troubleshooting

### Application Insights

The application has been configured with Azure Application Insights for monitoring:

1. Go to the Azure Portal
2. Navigate to your resource group
3. Open the "pd-management-insights" Application Insights resource
4. View traces, metrics, and performance data

### Container Logs

To view container logs:

1. Go to the Azure Portal
2. Navigate to your Container App
3. Select "Logs" from the left menu
4. View application logs or Container App system logs

## Database Management

### Connecting to Azure PostgreSQL

```bash
# Connect to the database with psql
psql -h pd-management-db-dev.postgres.database.azure.com -U <ADMIN_USER> -d pd_management
```

### Running Migrations

Migrations will run automatically during deployment. To run them manually:

```bash
# Set environment variables
export AZURE_DEPLOYMENT=true
export POSTGRES_HOST=pd-management-db-dev.postgres.database.azure.com
export POSTGRES_USER=<ADMIN_USER>
export POSTGRES_PASSWORD=<ADMIN_PASSWORD>
export POSTGRES_DB=pd_management

# Run migrations
cd backend
alembic upgrade head
```

## Security Considerations

1. **Connection Strings**: All sensitive connection strings are stored as GitHub secrets
2. **Database Firewall**: The Azure PostgreSQL server is configured to only allow connections from Azure services
3. **HTTPS**: All endpoints use HTTPS enforced by Azure Container Apps
4. **Authentication**: JWT-based authentication is used for API access

## Scaling

The application is configured to automatically scale:

- Backend: 1-3 replicas based on HTTP traffic
- Frontend: 1-3 replicas based on HTTP traffic
- Database: Standard_B1ms tier (can be upgraded as needed)

To adjust scaling parameters, modify the resource settings in the GitHub Actions workflow file.
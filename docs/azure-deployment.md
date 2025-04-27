# Azure Deployment Guide for PeritonealDialysisApp

This document provides details on Azure resource requirements, deployment process, and troubleshooting common issues.

## Required Azure Resources

The application uses the following Azure resources:

1. **Azure Container Registry (ACR)** - Stores Docker images for the application
2. **Azure Container Apps** - Hosts the containerized applications:
   - Frontend Angular application
   - Backend FastAPI application 
   - HAPI FHIR server
3. **Azure PostgreSQL Flexible Server** - Database for application data
4. **Azure Storage Account** - For HAPI FHIR data persistence
5. **Azure Application Insights** - For monitoring and logging
6. **Azure Log Analytics Workspace** - For centralized logging

## Required Permissions

The service principal used for GitHub Actions deployment requires the following permissions:

1. **Contributor** role at the resource group level (minimum)
2. **Resource Provider Registration** permissions if registering providers through CI/CD:
   - Microsoft.Storage/register/action
   - Microsoft.App/register/action
   - Microsoft.OperationalInsights/register/action
   - Microsoft.Insights/register/action
   - Microsoft.ContainerRegistry/register/action
   - Microsoft.DBforPostgreSQL/register/action

Alternatively, the required resource providers can be pre-registered by a subscription administrator.

## Setting Up the Service Principal

```bash
# Create a resource group if it doesn't exist
az group create --name pd-management-dev --location eastus2

# Create a service principal with Contributor role
az ad sp create-for-rbac \
  --name "pd-management-app-deploy" \
  --role Contributor \
  --scopes /subscriptions/<subscription-id>/resourceGroups/pd-management-dev \
  --sdk-auth

# Output will include client_id, client_secret, tenant_id - save these for GitHub Secrets
```

## GitHub Secrets Configuration

Set the following secrets in your GitHub repository:

- `AZURE_CLIENT_ID` - Service principal client ID
- `AZURE_TENANT_ID` - Azure tenant ID
- `AZURE_SUBSCRIPTION_ID` - Azure subscription ID
- `POSTGRES_ADMIN_USER` - PostgreSQL admin username
- `POSTGRES_ADMIN_PASSWORD` - PostgreSQL admin password

## Deployment Process

The deployment process consists of four main steps:

1. **Infrastructure Deployment** - Deploy Azure resources using Bicep template
2. **Build Container Images** - Build and push Docker images to ACR
3. **Deploy Applications** - Deploy container images to Container Apps
4. **Configuration** - Configure networking, environment variables, etc.

## Common Issues and Troubleshooting

### Missing Resource Provider Registration

**Error:**
```
The subscription is not registered to use namespace 'Microsoft.Storage'
```

**Solution:**
1. Pre-register providers manually with an account that has sufficient permissions:
   ```bash
   az provider register --namespace Microsoft.Storage
   az provider register --namespace Microsoft.App
   az provider register --namespace Microsoft.OperationalInsights
   az provider register --namespace Microsoft.Insights
   az provider register --namespace Microsoft.ContainerRegistry
   az provider register --namespace Microsoft.DBforPostgreSQL
   ```

2. OR grant your service principal the User Access Administrator role:
   ```bash
   az role assignment create --assignee "<service-principal-object-id>" --role "User Access Administrator" --scope "/subscriptions/<subscription-id>"
   ```

### Authentication Errors

**Error:**
```
AuthorizationFailed: The client does not have authorization to perform action...
```

**Solution:**
Check the role assignments for your service principal:
```bash
az role assignment list --assignee "<service-principal-client-id>"
```

### Bicep Template Validation Errors

**Error:**
```
BCP037: The property "volumeMounts" is not allowed on objects of type "Template"
```

**Solution:**
Review and update your Bicep template to ensure properties are defined at the correct scope level.

## Monitoring Deployed Resources

To monitor your deployed resources:

```bash
# Get Container App logs
az containerapp logs show -g pd-management-dev -n pd-management-backend

# Check Container App status
az containerapp show -g pd-management-dev -n pd-management-backend --query "properties.provisioningState"

# Monitor PostgreSQL server performance
az postgres flexible-server show-performance-insight -g pd-management-dev -n <server-name>
```

## Scaling and Performance Considerations

The deployed resources are configured with the following scaling parameters:

- **Frontend Container App:** 1-3 replicas based on HTTP load
- **Backend Container App:** 1-3 replicas based on HTTP load
- **HAPI FHIR Container App:** 1-2 replicas
- **PostgreSQL Server:** Burstable B2s tier (2 vCPUs, 4GB RAM)
#!/bin/bash

# Deployment script for Peritoneal Dialysis Application Azure Infrastructure

# Variables
RESOURCE_GROUP_NAME="pd-management-rg"
LOCATION="eastus"
ENVIRONMENT=${1:-dev}  # Default to 'dev' if not provided

echo "Deploying infrastructure for environment: $ENVIRONMENT"

# Create resource group if it doesn't exist
if [ $(az group exists --name $RESOURCE_GROUP_NAME) = false ]; then
  echo "Creating resource group: $RESOURCE_GROUP_NAME"
  az group create --name $RESOURCE_GROUP_NAME --location $LOCATION
else
  echo "Using existing resource group: $RESOURCE_GROUP_NAME"
fi

# Prompt for PostgreSQL admin credentials
read -p "PostgreSQL Admin Username: " POSTGRES_ADMIN_LOGIN
read -sp "PostgreSQL Admin Password: " POSTGRES_ADMIN_PASSWORD
echo

# Validate the deployment first (what-if)
echo "Validating deployment..."
az deployment group what-if \
  --resource-group $RESOURCE_GROUP_NAME \
  --template-file main.bicep \
  --parameters \
    environmentName=$ENVIRONMENT \
    postgresAdminLogin=$POSTGRES_ADMIN_LOGIN \
    postgresAdminPassword=$POSTGRES_ADMIN_PASSWORD

# Confirm deployment
read -p "Continue with deployment? (y/n): " CONFIRM
if [[ $CONFIRM != "y" && $CONFIRM != "Y" ]]; then
  echo "Deployment cancelled"
  exit 0
fi

# Execute the deployment
echo "Deploying resources..."
az deployment group create \
  --resource-group $RESOURCE_GROUP_NAME \
  --template-file main.bicep \
  --parameters \
    environmentName=$ENVIRONMENT \
    postgresAdminLogin=$POSTGRES_ADMIN_LOGIN \
    postgresAdminPassword=$POSTGRES_ADMIN_PASSWORD

# Output URLs
echo "Deployment completed!"
echo "Access your application at the URLs provided in the outputs above."
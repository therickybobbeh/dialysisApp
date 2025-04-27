#!/bin/bash

# Deployment script for Peritoneal Dialysis Application Azure Infrastructure

# Exit on error
set -e

# Variables
RESOURCE_GROUP_NAME="pd-management-rg"
PRIMARY_LOCATION="eastus"
ENVIRONMENT=${1:-dev}  # Default to 'dev' if not provided
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Available regions for PostgreSQL servers
AVAILABLE_REGIONS=("eastus" "westus2" "centralus" "northeurope" "westeurope" "southcentralus" "southeastasia")
SELECTED_LOCATION=$PRIMARY_LOCATION

echo "Deploying infrastructure for environment: $ENVIRONMENT"

# Function to handle errors
handle_error() {
  echo "Error occurred on line $1"
  echo "Last command: $2"
  echo "Exiting..."
}

# Set up error handling
trap 'handle_error $LINENO "$BASH_COMMAND"' ERR

# Create resource group if it doesn't exist
echo "Checking resource group: $RESOURCE_GROUP_NAME"
if [ $(az group exists --name $RESOURCE_GROUP_NAME) = false ]; then
  echo "Creating resource group: $RESOURCE_GROUP_NAME in $SELECTED_LOCATION"
  az group create --name $RESOURCE_GROUP_NAME --location $SELECTED_LOCATION
else
  echo "Using existing resource group: $RESOURCE_GROUP_NAME"
fi

# Prompt for PostgreSQL admin credentials
echo "Enter PostgreSQL admin credentials:"
read -p "PostgreSQL Admin Username: " POSTGRES_ADMIN_LOGIN
read -sp "PostgreSQL Admin Password: " POSTGRES_ADMIN_PASSWORD
echo

# Function to deploy infrastructure (Phase 1)
deploy_infrastructure() {
  local region=$1
  echo "Deploying infrastructure in region: $region"
  
  # Deploy infrastructure - exclude container apps
  az deployment group create \
    --resource-group $RESOURCE_GROUP_NAME \
    --template-file "$SCRIPT_DIR/infrastructure.bicep" \
    --parameters \
      environmentName=$ENVIRONMENT \
      location=$region \
      postgresAdminLogin=$POSTGRES_ADMIN_LOGIN \
      postgresAdminPassword=$POSTGRES_ADMIN_PASSWORD
  
  # Get ACR name from outputs
  ACR_NAME=$(az deployment group show \
    --resource-group $RESOURCE_GROUP_NAME \
    --name infrastructure \
    --query "properties.outputs.acrName.value" \
    --output tsv)
    
  echo "Azure Container Registry created: $ACR_NAME.azurecr.io"
  return $?
}

# Function to build and push container images
build_and_push_images() {
  local acr_name=$1
  echo "Building and pushing container images to $acr_name.azurecr.io"
  
  # Login to ACR
  echo "Logging in to ACR..."
  az acr login --name $acr_name
  
  # Build and push backend image
  echo "Building and pushing backend image..."
  docker build -t "$acr_name.azurecr.io/pd-management-backend:latest" -f "$PROJECT_ROOT/backend/Dockerfile" "$PROJECT_ROOT/backend"
  docker push "$acr_name.azurecr.io/pd-management-backend:latest"
  
  # Build and push frontend image
  echo "Building and pushing frontend image..."
  docker build -t "$acr_name.azurecr.io/pd-management-frontend:latest" -f "$PROJECT_ROOT/dialysis-app-ui/Dockerfile" "$PROJECT_ROOT/dialysis-app-ui"
  docker push "$acr_name.azurecr.io/pd-management-frontend:latest"
  
  echo "Container images successfully pushed to ACR"
}

# Function to deploy container apps (Phase 2)
deploy_container_apps() {
  local region=$1
  local acr_name=$2
  echo "Deploying container apps in region: $region"
  
  # Deploy container apps
  az deployment group create \
    --resource-group $RESOURCE_GROUP_NAME \
    --template-file "$SCRIPT_DIR/container-apps.bicep" \
    --parameters \
      environmentName=$ENVIRONMENT \
      location=$region \
      acrName=$acr_name \
      postgresAdminLogin=$POSTGRES_ADMIN_LOGIN \
      postgresAdminPassword=$POSTGRES_ADMIN_PASSWORD
      
  echo "Container apps deployed successfully"
}

# Function to try deployment in different regions
try_deployment() {
  local region=$1
  echo "Attempting deployment in region: $region"
  
  # Validate the deployment first (what-if)
  echo "Validating infrastructure deployment..."
  az deployment group what-if \
    --resource-group $RESOURCE_GROUP_NAME \
    --template-file "$SCRIPT_DIR/infrastructure.bicep" \
    --parameters \
      environmentName=$ENVIRONMENT \
      location=$region \
      postgresAdminLogin=$POSTGRES_ADMIN_LOGIN \
      postgresAdminPassword=$POSTGRES_ADMIN_PASSWORD
  
  # Return the validation status
  return $?
}

# Try deployment in each region until one works
deployment_successful=false
for region in "${AVAILABLE_REGIONS[@]}"; do
  echo "Trying region: $region"
  if try_deployment $region; then
    SELECTED_LOCATION=$region
    deployment_successful=true
    break
  else
    echo "Deployment validation failed in region $region, trying next region..."
  fi
done

if [ "$deployment_successful" = false ]; then
  echo "Deployment failed in all available regions. Please check your subscription limits or try again later."
  exit 1
fi

# Confirm deployment
read -p "Continue with deployment in $SELECTED_LOCATION? (y/n): " CONFIRM
if [[ $CONFIRM != "y" && $CONFIRM != "Y" ]]; then
  echo "Deployment cancelled"
  exit 0
fi

# Phase 1: Deploy infrastructure (ACR, PostgreSQL, Log Analytics)
echo "Phase 1: Deploying infrastructure resources..."
deploy_infrastructure $SELECTED_LOCATION
echo "Infrastructure resources deployed successfully"

# Build and push Docker images
echo "Building and pushing Docker images to Azure Container Registry..."
build_and_push_images $ACR_NAME

# Phase 2: Deploy container apps
echo "Phase 2: Deploying container apps..."
deploy_container_apps $SELECTED_LOCATION $ACR_NAME

# Output URLs
echo "Deployment completed!"
echo "Deployment region: $SELECTED_LOCATION"
echo "Access your application at the URLs provided in the outputs above."
#!/bin/bash
# Peritoneal Dialysis App Deployment Script
# This script builds and deploys the application to Azure Container Apps

set -e  # Exit immediately if a command exits with a non-zero status

# Get the absolute path to the project root directory
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
echo "🔍 Project root: $PROJECT_ROOT"

# Configuration
RESOURCE_GROUP="pd-management-dev"  # Replace with your resource group name
ACR_NAME=""  # Will be populated from bicep output
FRONTEND_APP_NAME="pd-management-frontend"
BACKEND_APP_NAME="pd-management-backend"
SUBSCRIPTION_ID=""  # Optional: Replace with your subscription ID

echo "🚀 Starting deployment process for Peritoneal Dialysis App"

# Step 1: Build images and push to ACR
build_and_push_images() {
  echo "📦 Building and pushing container images to ACR"
  
  # Build frontend
  echo "Building frontend image..."
  cd "$PROJECT_ROOT/dialysis-app-ui"
  
  # Verify the directory exists and we're in the right place
  if [ ! -f "Dockerfile" ]; then
    echo "❌ Error: Frontend Dockerfile not found at $(pwd)/Dockerfile"
    echo "Directory contents:"
    ls -la
    exit 1
  fi
  
  docker build -t "$ACR_NAME.azurecr.io/$FRONTEND_APP_NAME:latest" .
  
  # Build backend
  echo "Building backend image..."
  cd "$PROJECT_ROOT"
  
  if [ ! -f "backend/Dockerfile" ]; then
    echo "❌ Error: Backend Dockerfile not found at $(pwd)/backend/Dockerfile"
    echo "Directory contents of backend:"
    ls -la backend
    exit 1
  fi
  
  docker build -t "$ACR_NAME.azurecr.io/$BACKEND_APP_NAME:latest" -f backend/Dockerfile .
  
  # Log in to ACR
  echo "Logging in to ACR..."
  az acr login --name "$ACR_NAME"
  
  # Push images
  echo "Pushing frontend image..."
  docker push "$ACR_NAME.azurecr.io/$FRONTEND_APP_NAME:latest"
  echo "Pushing backend image..."
  docker push "$ACR_NAME.azurecr.io/$BACKEND_APP_NAME:latest"
}

# Step 2: Deploy infrastructure
deploy_infrastructure() {
  echo "🏗️ Deploying infrastructure using Bicep"
  cd "$PROJECT_ROOT/infra"
  
  # Verify the bicep file exists
  if [ ! -f "main.bicep" ]; then
    echo "❌ Error: main.bicep not found at $(pwd)/main.bicep"
    echo "Directory contents:"
    ls -la
    exit 1
  fi
  
  # Set subscription if provided
  if [[ -n "$SUBSCRIPTION_ID" ]]; then
    az account set --subscription "$SUBSCRIPTION_ID"
  fi
  
  # Deploy Bicep template with useInitialPlaceholderImages=false to use our custom images
  az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file main.bicep \
    --parameters useInitialPlaceholderImages=false \
    --output json
    
  # Get ACR login server from deployment output
  ACR_NAME=$(az deployment group show \
    --resource-group "$RESOURCE_GROUP" \
    --name main \
    --query "properties.outputs.acrLoginServer.value" \
    --output tsv)
    
  ACR_NAME=${ACR_NAME/.azurecr.io/}
  echo "ACR Name: $ACR_NAME"
}

# Step 3: Update container apps to use the latest images
restart_container_apps() {
  echo "🔄 Restarting container apps to pick up the latest images"
  
  az containerapp update \
    --name "$FRONTEND_APP_NAME" \
    --resource-group "$RESOURCE_GROUP"
    
  az containerapp update \
    --name "$BACKEND_APP_NAME" \
    --resource-group "$RESOURCE_GROUP"
}

# Main execution flow
echo "Step 1: Deploying infrastructure..."
deploy_infrastructure

echo "Step 2: Building and pushing images..."
build_and_push_images

echo "Step 3: Restarting container apps..."
restart_container_apps

echo "✅ Deployment completed successfully!"
echo "Frontend URL: $(az containerapp show --name "$FRONTEND_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "properties.configuration.ingress.fqdn" --output tsv)"
echo "Backend URL: $(az containerapp show --name "$BACKEND_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "properties.configuration.ingress.fqdn" --output tsv)"
// Peritoneal Dialysis Application - Azure Infrastructure
// Phase 2: Container Apps deployment

// Parameters with default values
@description('The environment name (dev, test, prod)')
param environmentName string = 'dev'

@description('The Azure region for all resources')
param location string = 'eastus2'

@description('The name of the Azure Container Registry')
param acrName string

@description('PostgreSQL administrator login')
@secure()
param postgresAdminLogin string

@description('PostgreSQL administrator password')
@secure()
param postgresAdminPassword string

@description('Application frontend and backend container names')
param backendContainerAppName string = 'pd-management-backend'
param frontendContainerAppName string = 'pd-management-frontend'

@description('Minimum and maximum replicas for container apps')
param frontendMinReplicas int = 1
param frontendMaxReplicas int = 3
param backendMinReplicas int = 1
param backendMaxReplicas int = 3

// Variables
var baseName = 'pd-management-${environmentName}'
var postgresServerName = '${baseName}-db'
var containerAppEnvironmentName = '${baseName}-env'
var logAnalyticsWorkspaceName = '${baseName}-logs'
var appInsightsName = '${baseName}-insights'

// Reference existing resources
resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' existing = {
  name: acrName
}

resource containerAppEnvironment 'Microsoft.App/managedEnvironments@2022-10-01' existing = {
  name: containerAppEnvironmentName
}

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' existing = {
  name: logAnalyticsWorkspaceName
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: appInsightsName
}

// Deploy container apps
resource backendContainerApp 'Microsoft.App/containerApps@2022-10-01' = {
  name: backendContainerAppName
  location: location
  properties: {
    managedEnvironmentId: containerAppEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8004
        allowInsecure: false
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
      }
      registries: [
        {
          server: '${acrName}.azurecr.io'
          username: acr.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: acr.listCredentials().passwords[0].value
        }
        {
          name: 'postgres-password'
          value: postgresAdminPassword
        }
      ]
    }
    template: {
      containers: [
        {
          name: backendContainerAppName
          image: '${acrName}.azurecr.io/${backendContainerAppName}:latest'
          resources: {
            cpu: '0.5'
            memory: '1.0Gi'
          }
          env: [
            {
              name: 'AZURE_DEPLOYMENT'
              value: 'true'
            }
            {
              name: 'ENABLE_APP_INSIGHTS'
              value: 'true'
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: appInsights.properties.ConnectionString
            }
            {
              name: 'LOG_LEVEL'
              value: 'INFO'
            }
            {
              name: 'POSTGRES_HOST'
              value: '${postgresServerName}.postgres.database.azure.com'
            }
            {
              name: 'POSTGRES_USER'
              value: postgresAdminLogin
            }
            {
              name: 'POSTGRES_PASSWORD'
              secretRef: 'postgres-password'
            }
            {
              name: 'POSTGRES_DB'
              value: 'pd_management'
            }
            {
              name: 'POSTGRES_PORT'
              value: '5432'
            }
            {
              name: 'DB_POOL_SIZE'
              value: '10'
            }
            {
              name: 'DB_MAX_OVERFLOW'
              value: '20'
            }
            {
              name: 'STRUCTURED_LOGGING'
              value: 'true'
            }
          ]
          probes: [
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: 8004
                scheme: 'HTTP'
              }
              initialDelaySeconds: 10
              periodSeconds: 30
              timeoutSeconds: 10
              successThreshold: 1
              failureThreshold: 3
            }
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 8004
                scheme: 'HTTP'
              }
              initialDelaySeconds: 30
              periodSeconds: 60
              timeoutSeconds: 10
              failureThreshold: 5
            }
          ]
        }
      ]
      scale: {
        minReplicas: backendMinReplicas
        maxReplicas: backendMaxReplicas
        rules: [
          {
            name: 'http-scale'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
}

resource frontendContainerApp 'Microsoft.App/containerApps@2022-10-01' = {
  name: frontendContainerAppName
  location: location
  properties: {
    managedEnvironmentId: containerAppEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 80
        allowInsecure: false
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
      }
      registries: [
        {
          server: '${acrName}.azurecr.io'
          username: acr.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        {
          name: 'acr-password'
          value: acr.listCredentials().passwords[0].value
        }
      ]
    }
    template: {
      containers: [
        {
          name: frontendContainerAppName
          image: '${acrName}.azurecr.io/${frontendContainerAppName}:latest'
          resources: {
            cpu: '0.25'
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'API_URL'
              value: 'https://${backendContainerApp.properties.configuration.ingress.fqdn}'
            }
            {
              name: 'ENVIRONMENT'
              value: environmentName
            }
          ]
          probes: [
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: 80
                scheme: 'HTTP'
              }
              initialDelaySeconds: 10
              periodSeconds: 30
              timeoutSeconds: 10
              successThreshold: 1
              failureThreshold: 3
            }
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 80
                scheme: 'HTTP'
              }
              initialDelaySeconds: 30
              periodSeconds: 60
              timeoutSeconds: 10
              failureThreshold: 5
            }
          ]
        }
      ]
      scale: {
        minReplicas: frontendMinReplicas
        maxReplicas: frontendMaxReplicas
        rules: [
          {
            name: 'http-scale'
            http: {
              metadata: {
                concurrentRequests: '20'
              }
            }
          }
        ]
      }
    }
  }
}

// Outputs
output backendUrl string = 'https://${backendContainerApp.properties.configuration.ingress.fqdn}'
output frontendUrl string = 'https://${frontendContainerApp.properties.configuration.ingress.fqdn}'
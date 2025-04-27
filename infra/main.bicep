// Peritoneal Dialysis Application - Complete Azure Infrastructure
// This file defines all the Azure resources needed for the application

// Parameters with default values
@description('The environment name (dev, test, prod)')
param environmentName string = 'dev'

@description('The Azure region for all resources')
param location string = 'eastus2' // Changed back to eastus2 since existing resources are there

@description('The SKU for Azure Container Registry')
param acrSku string = 'Basic'

@description('PostgreSQL administrator login')
@secure()
param postgresAdminLogin string

@description('PostgreSQL administrator password')
@secure()
param postgresAdminPassword string

@description('Use existing PostgreSQL server rather than creating a new one')
param useExistingPostgresServer bool = true

@description('Name of the existing PostgreSQL server if useExistingPostgresServer is true')
param existingPostgresServerName string = 'pdmanagementdevdb'

@description('Indicates whether we should use the existing Log Analytics workspace')
param useExistingLogAnalytics bool = true

@description('Application frontend and backend container names')
param backendContainerAppName string = 'pd-management-backend'
param frontendContainerAppName string = 'pd-management-frontend'

@description('Minimum and maximum replicas for container apps')
param frontendMinReplicas int = 1
param frontendMaxReplicas int = 3
param backendMinReplicas int = 1
param backendMaxReplicas int = 3

// Generate a unique suffix based on resourceGroup().id
var uniqueSuffix = uniqueString(resourceGroup().id)

// Variables for resource naming
var baseName = 'pd-management-${environmentName}'
var acrName = replace('pdmgmtacr${environmentName}${uniqueSuffix}', '-', '')  // Made ACR name unique
var postgresServerName = useExistingPostgresServer ? existingPostgresServerName : '${baseName}-db'
var containerAppEnvironmentName = '${baseName}-env'
var logAnalyticsWorkspaceName = '${baseName}-logs'
var appInsightsName = '${baseName}-insights'

// Reference existing Log Analytics workspace
resource existingLogAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' existing = if (useExistingLogAnalytics) {
  name: logAnalyticsWorkspaceName
}

// Log Analytics workspace for monitoring
resource newLogAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = if (!useExistingLogAnalytics) {
  name: logAnalyticsWorkspaceName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Application Insights for application monitoring
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: useExistingLogAnalytics ? existingLogAnalyticsWorkspace.id : newLogAnalyticsWorkspace.id
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// Azure Container Registry for storing container images
resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: acrName
  location: location
  sku: {
    name: acrSku
  }
  properties: {
    adminUserEnabled: true
    anonymousPullEnabled: false
    dataEndpointEnabled: false
    networkRuleBypassOptions: 'AzureServices'
    publicNetworkAccess: 'Enabled'
    zoneRedundancy: 'Disabled'
  }
}

// Reference existing PostgreSQL server
resource existingPostgres 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' existing = if (useExistingPostgresServer) {
  name: existingPostgresServerName
}

// PostgreSQL Flexible Server - Only create if not using existing
resource newPostgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' = if (!useExistingPostgresServer) {
  name: postgresServerName
  location: location
  sku: {
    name: 'Standard_B2s' // Using a more cost-effective SKU for development
    tier: 'Burstable'
  }
  properties: {
    version: '16' // Using PostgreSQL version 16
    administratorLogin: postgresAdminLogin
    administratorLoginPassword: postgresAdminPassword
    storage: {
      storageSizeGB: 32 // 32 GB storage for development
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled' // Disabling HA for cost efficiency
    }
  }

  // Create default database
  resource database 'databases' = {
    name: 'pd_management'
  }

  // Configure firewall to allow Azure services
  resource firewallRule 'firewallRules' = {
    name: 'AllowAzureServices'
    properties: {
      startIpAddress: '0.0.0.0'
      endIpAddress: '0.0.0.0'
    }
  }
}

// Container Apps Environment for hosting containerized applications
resource containerAppEnvironment 'Microsoft.App/managedEnvironments@2022-10-01' = {
  name: containerAppEnvironmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: useExistingLogAnalytics ? existingLogAnalyticsWorkspace.properties.customerId : newLogAnalyticsWorkspace.properties.customerId
        sharedKey: useExistingLogAnalytics ? existingLogAnalyticsWorkspace.listKeys().primarySharedKey : newLogAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
  }
}

// Backend Container App for hosting the Python FastAPI backend
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
          server: '${acr.name}.azurecr.io'
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
          image: '${acr.name}.azurecr.io/${backendContainerAppName}:latest'
          resources: {
            cpu: json('0.5') // Fixed: Changed string to number using json() for backward compatibility
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
              value: useExistingPostgresServer 
              ? '${existingPostgres.name}.postgres.database.azure.com'
              : '${newPostgresServer.name}.postgres.database.azure.com'
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

// Frontend Container App for hosting the Angular UI
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
          server: '${acr.name}.azurecr.io'
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
          image: '${acr.name}.azurecr.io/${frontendContainerAppName}:latest'
          resources: {
            cpu: json('0.25') // Fixed: Changed string to number using json() for backward compatibility
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
output acrLoginServer string = '${acr.name}.azurecr.io'
output postgresServerFqdn string = useExistingPostgresServer 
  ? (existingPostgres.properties.fullyQualifiedDomainName ?? '${existingPostgres.name}.postgres.database.azure.com')
  : newPostgresServer.properties.fullyQualifiedDomainName
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output appInsightsConnectionString string = appInsights.properties.ConnectionString

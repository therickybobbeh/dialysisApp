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

@description('Use placeholder images for initial deployment (true) or expect images to exist (false)')
param useInitialPlaceholderImages bool = true

@description('Application frontend and backend container names')
param backendContainerAppName string = 'pd-management-backend'
param frontendContainerAppName string = 'pd-management-frontend'
param hapiFhirServerName string = 'pd-management-hapi-fhir'

@description('Minimum and maximum replicas for container apps')
param frontendMinReplicas int = 1
param frontendMaxReplicas int = 3
param backendMinReplicas int = 1
param backendMaxReplicas int = 3
param hapiFhirMinReplicas int = 1
param hapiFhirMaxReplicas int = 2

// Generate a unique suffix based on resourceGroup().id
var uniqueSuffix = uniqueString(resourceGroup().id)

// Variables for resource naming
var baseName = 'pd-management-${environmentName}'
var acrName = replace('pdmgmtacr${environmentName}${uniqueSuffix}', '-', '')  // Made ACR name unique
var postgresServerName = useExistingPostgresServer ? existingPostgresServerName : '${baseName}-db'
var containerAppEnvironmentName = '${baseName}-env'
var logAnalyticsWorkspaceName = '${baseName}-logs'
var appInsightsName = '${baseName}-insights'

// A placeholder image to use for initial deployment
// The mcr.microsoft.com/azuredocs/containerapps-helloworld is publicly available and can be used initially
// The app will be updated with actual images after they are pushed to ACR
var placeholderImage = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

// HAPI FHIR server image from Docker Hub
var hapiFhirImage = 'hapiproject/hapi:latest'

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

// Storage account for persistent HAPI FHIR data
resource hapiStorageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: toLower(replace('hapifhir${environmentName}${uniqueSuffix}', '-', ''))
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
  }
}

// File share for HAPI FHIR data persistence
resource hapiFileShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2022-09-01' = {
  name: '${hapiStorageAccount.name}/default/hapi-data'
  properties: {
    shareQuota: 5 // 5GB
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

// HAPI FHIR Server Container App
resource hapiFhirContainerApp 'Microsoft.App/containerApps@2022-10-01' = {
  name: hapiFhirServerName
  location: location
  properties: {
    managedEnvironmentId: containerAppEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8080
        allowInsecure: false
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
      }
      secrets: [
        {
          name: 'storage-key'
          value: hapiStorageAccount.listKeys().keys[0].value
        }
      ]
    }
    template: {
      containers: [
        {
          name: hapiFhirServerName
          image: hapiFhirImage
          resources: {
            cpu: json('1.0')
            memory: '2.0Gi'
          }
          env: [
            {
              name: 'HAPI_FHIR_JPA_SERVER'
              value: 'HAPI_JPA_SERVER'
            }
            {
              name: 'SERVER_ADDRESS'
              value: '0.0.0.0'
            }
            {
              name: 'SERVER_PORT'
              value: '8080'
            }
            {
              name: 'SPRING_CONFIG_LOCATION'
              value: 'file:///hapi-data/application.yaml'
            }
          ]
          volumeMounts: [
            {
              volumeName: 'hapi-data'
              mountPath: '/hapi-data'
            }
          ]
        }
      ]
      scale: {
        minReplicas: hapiFhirMinReplicas
        maxReplicas: hapiFhirMaxReplicas
      }
      volumes: [
        {
          name: 'hapi-data'
          storageType: 'AzureFile'
          storageName: 'hapi-storage'
        }
      ]
      volumeMounts: [
        {
          volumeName: 'hapi-data'
          mountPath: '/hapi-data'
        }
      ]
    }
  }
}

// Storage config for HAPI FHIR server
resource hapiStorage 'Microsoft.App/managedEnvironments/storages@2022-10-01' = {
  name: 'hapi-storage'
  parent: containerAppEnvironment
  properties: {
    azureFile: {
      accountName: hapiStorageAccount.name
      accountKey: hapiStorageAccount.listKeys().keys[0].value
      shareName: 'hapi-data'
      accessMode: 'ReadWrite'
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
        targetPort: useInitialPlaceholderImages ? 80 : 8004 // The placeholder uses port 80, our app uses 8004
        allowInsecure: false
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
      }
      registries: useInitialPlaceholderImages ? [] : [
        {
          server: '${acr.name}.azurecr.io'
          username: acr.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: useInitialPlaceholderImages ? [] : [
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
          image: useInitialPlaceholderImages ? placeholderImage : '${acr.name}.azurecr.io/${backendContainerAppName}:latest'
          resources: {
            cpu: json('0.5') // Fixed: Changed string to number using json() for backward compatibility
            memory: '1.0Gi'
          }
          env: useInitialPlaceholderImages ? [] : [
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
            // ADDING HAPI FHIR SERVER CONNECTION
            {
              name: 'HAPI_BASE_URL'
              value: 'https://${hapiFhirContainerApp.properties.configuration.ingress.fqdn}/fhir/'
            }
          ]
          // Only add probes if we're not using placeholder images
          probes: useInitialPlaceholderImages ? [] : [
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
        targetPort: 80 // Both the placeholder and our app use port 80
        allowInsecure: false
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
      }
      registries: useInitialPlaceholderImages ? [] : [
        {
          server: '${acr.name}.azurecr.io'
          username: acr.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: useInitialPlaceholderImages ? [] : [
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
          image: useInitialPlaceholderImages ? placeholderImage : '${acr.name}.azurecr.io/${frontendContainerAppName}:latest'
          resources: {
            cpu: json('0.25') // Fixed: Changed string to number using json() for backward compatibility
            memory: '0.5Gi'
          }
          env: useInitialPlaceholderImages ? [] : [
            {
              name: 'API_URL'
              value: 'https://${backendContainerApp.properties.configuration.ingress.fqdn}'
            }
            {
              name: 'ENVIRONMENT'
              value: environmentName
            }
          ]
          // Only add probes if we're not using placeholder images
          probes: useInitialPlaceholderImages ? [] : [
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
output hapiFhirUrl string = 'https://${hapiFhirContainerApp.properties.configuration.ingress.fqdn}'
output acrLoginServer string = '${acr.name}.azurecr.io'
output postgresServerFqdn string = useExistingPostgresServer 
  ? (existingPostgres.properties.fullyQualifiedDomainName ?? '${existingPostgres.name}.postgres.database.azure.com')
  : newPostgresServer.properties.fullyQualifiedDomainName
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output appInsightsConnectionString string = appInsights.properties.ConnectionString

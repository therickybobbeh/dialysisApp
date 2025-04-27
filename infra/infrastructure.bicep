// Peritoneal Dialysis Application - Azure Infrastructure
// Phase 1: Core infrastructure resources

// Parameters with default values
@description('The environment name (dev, test, prod)')
param environmentName string = 'dev'

@description('The Azure region for all resources')
param location string = 'eastus2'

@description('The SKU for Azure Container Registry')
param acrSku string = 'Basic'

@description('PostgreSQL administrator login')
@secure()
param postgresAdminLogin string

@description('PostgreSQL administrator password')
@secure()
param postgresAdminPassword string

@description('The PostgreSQL version')
param postgresVersion string = '11'  // Version 11 is supported for Single Server

// Generate a unique suffix based on resourceGroup().id
var uniqueSuffix = uniqueString(resourceGroup().id)

// Variables
var baseName = 'pd-management-${environmentName}'
var acrName = take(replace('pdmgmtacr${environmentName}${uniqueSuffix}', '-', ''), 50)  // Ensure unique name within the character limit
var postgresServerName = '${baseName}-db'
var containerAppEnvironmentName = '${baseName}-env'
var logAnalyticsWorkspaceName = '${baseName}-logs'
var appInsightsName = '${baseName}-insights'

// Resource definitions
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
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

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

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

// PostgreSQL Single Server
resource postgresServer 'Microsoft.DBforPostgreSQL/servers@2017-12-01' = {
  name: postgresServerName
  location: location
  sku: {
    name: 'B_Gen5_1'   // Basic tier SKU
    tier: 'Basic'
    capacity: 1
    family: 'Gen5'
  }
  properties: {
    version: postgresVersion
    administratorLogin: postgresAdminLogin
    administratorLoginPassword: postgresAdminPassword
    storageProfile: {
      storageMB: 32768          // 32 GB
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    sslEnforcement: 'Enabled'
  }

  // create default db
  resource database 'databases@2017-12-01' = {
    name: 'pd_management'
  }

  resource firewallRule 'firewallRules@2017-12-01' = {
    name: 'AllowAzureServices'
    properties: {
      startIpAddress: '0.0.0.0'
      endIpAddress: '0.0.0.0'
    }
  }
}

resource containerAppEnvironment 'Microsoft.App/managedEnvironments@2022-10-01' = {
  name: containerAppEnvironmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
  }
}

// Outputs
output acrName string = acr.name
output acrLoginServer string = '${acr.name}.azurecr.io'
output postgresServerName string = postgresServer.name
output containerAppEnvironmentId string = containerAppEnvironment.id
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output logAnalyticsWorkspaceId string = logAnalyticsWorkspace.id
@description('Base name used for all resources (lowercase, no spaces)')
param appName string = 'turbincontrol'

@description('Azure region for all resources')
param location string = resourceGroup().location

// ── Azure Container Registry ──────────────────────────────────────────────
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: '${appName}acr'
  location: location
  sku: {
    name: 'Basic'  // Cheapest tier — fine for a student project
  }
  properties: {
    adminUserEnabled: true
  }
}

// ── Log Analytics (required by Container Apps) ───────────────────────────
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${appName}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// ── Container Apps Environment ────────────────────────────────────────────
resource containerEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: '${appName}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// ── Container App ─────────────────────────────────────────────────────────
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: appName
  location: location
  properties: {
    managedEnvironmentId: containerEnv.id
    configuration: {
      ingress: {
        external: true       // Public HTTPS endpoint
        targetPort: 8000
        transport: 'http'
      }
      registries: [
        {
          server: acr.properties.loginServer
          username: acr.name
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
          name: appName
          image: '${acr.properties.loginServer}/${appName}:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0   // Scale to zero when idle — saves cost on student account
        maxReplicas: 3
      }
    }
  }
}

// ── Outputs ────────────────────────────────────────────────────────────────
output acrLoginServer string = acr.properties.loginServer
output appUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'

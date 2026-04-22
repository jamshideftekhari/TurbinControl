# One-time Azure provisioning script.
# Run this once from your local machine before the first deploy.
# Prerequisites: Azure CLI (az) installed and logged in via: az login

$ErrorActionPreference = "Stop"

# Configuration - edit these
$APP_NAME       = "turbincontrol"
$RESOURCE_GROUP = "$APP_NAME-rg"
$LOCATION       = "westeurope"    # Change to a region close to you

# Register required Azure resource providers (safe to run even if already registered)
Write-Host "==> Registering resource providers..." -ForegroundColor Cyan
az provider register --namespace Microsoft.App             --wait
az provider register --namespace Microsoft.ContainerRegistry --wait
az provider register --namespace Microsoft.OperationalInsights --wait

Write-Host "==> Creating resource group: $RESOURCE_GROUP" -ForegroundColor Cyan
az group create --name $RESOURCE_GROUP --location $LOCATION | Out-Null

Write-Host "==> Deploying Azure infrastructure (Bicep) - this takes ~2 minutes..." -ForegroundColor Cyan
az deployment group create `
    --resource-group $RESOURCE_GROUP `
    --template-file "$PSScriptRoot\main.bicep" `
    --parameters "appName=$APP_NAME"

# Check deployment succeeded
$state = az deployment group show `
    --resource-group $RESOURCE_GROUP `
    --name main `
    --query "properties.provisioningState" `
    -o tsv

if ($state -ne "Succeeded") {
    Write-Host "ERROR: Deployment did not succeed (state: $state). Check errors above." -ForegroundColor Red
    exit 1
}

# Extract outputs using az CLI query (avoids PowerShell JSON parsing)
$ACR_SERVER = (az deployment group show `
    --resource-group $RESOURCE_GROUP `
    --name main `
    --query "properties.outputs.acrLoginServer.value" `
    -o tsv).Trim()

$APP_URL = (az deployment group show `
    --resource-group $RESOURCE_GROUP `
    --name main `
    --query "properties.outputs.appUrl.value" `
    -o tsv).Trim()

Write-Host ""
Write-Host "==> Infrastructure ready." -ForegroundColor Green
Write-Host "    ACR login server : $ACR_SERVER"
Write-Host "    App URL          : $APP_URL"

Write-Host ""
Write-Host "==> Creating GitHub Actions service principal..." -ForegroundColor Cyan
$subscriptionId = (az account show --query id -o tsv).Trim()
$scope = "/subscriptions/$subscriptionId/resourceGroups/$RESOURCE_GROUP"

$spJson = (az ad sp create-for-rbac `
    --name "$APP_NAME-github-sp" `
    --role contributor `
    --scopes $scope `
    --sdk-auth) -join ""

$sep = "=" * 67
Write-Host ""
Write-Host $sep -ForegroundColor Yellow
Write-Host "Add the following secrets to your GitHub repository:" -ForegroundColor Yellow
Write-Host "  repo -> Settings -> Secrets and variables -> Actions -> New secret" -ForegroundColor Yellow
Write-Host $sep -ForegroundColor Yellow
Write-Host ""
Write-Host "AZURE_CREDENTIALS     (paste the entire JSON block below)"
Write-Host $spJson
Write-Host ""
Write-Host "AZURE_RESOURCE_GROUP  $RESOURCE_GROUP"
Write-Host "ACR_NAME              ${APP_NAME}acr"
Write-Host "ACR_LOGIN_SERVER      $ACR_SERVER"
Write-Host "CONTAINER_APP_NAME    $APP_NAME"
Write-Host ""
Write-Host $sep -ForegroundColor Yellow

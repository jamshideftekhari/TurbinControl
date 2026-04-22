#!/usr/bin/env bash
# One-time Azure provisioning script.
# Run this once from your local machine before the first deploy.
# Requires: Azure CLI (az) logged in with your student account.

set -euo pipefail

# ── Configuration — edit these ────────────────────────────────────────────
APP_NAME="turbincontrol"
RESOURCE_GROUP="${APP_NAME}-rg"
LOCATION="westeurope"          # Change to a region close to you
# ──────────────────────────────────────────────────────────────────────────

echo "==> Creating resource group: $RESOURCE_GROUP"
az group create --name "$RESOURCE_GROUP" --location "$LOCATION"

echo "==> Deploying Azure infrastructure (Bicep)..."
DEPLOY=$(az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file "$(dirname "$0")/main.bicep" \
  --parameters appName="$APP_NAME" \
  --output json)

ACR_SERVER=$(echo "$DEPLOY" | python3 -c "import sys,json; print(json.load(sys.stdin)['properties']['outputs']['acrLoginServer']['value'])")
APP_URL=$(echo "$DEPLOY"    | python3 -c "import sys,json; print(json.load(sys.stdin)['properties']['outputs']['appUrl']['value'])")

echo "==> Infrastructure ready."
echo "    ACR login server : $ACR_SERVER"
echo "    App URL          : $APP_URL"

echo ""
echo "==> Creating GitHub Actions service principal..."
SP=$(az ad sp create-for-rbac \
  --name "${APP_NAME}-github-sp" \
  --role contributor \
  --scopes "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP" \
  --sdk-auth)

echo ""
echo "==================================================================="
echo "Add the following as GitHub repository secrets:"
echo "==================================================================="
echo ""
echo "AZURE_CREDENTIALS      (paste the entire JSON block below)"
echo "$SP"
echo ""
echo "AZURE_RESOURCE_GROUP   $RESOURCE_GROUP"
echo "ACR_NAME               ${APP_NAME}acr"
echo "ACR_LOGIN_SERVER       $ACR_SERVER"
echo "CONTAINER_APP_NAME     $APP_NAME"
echo "==================================================================="
echo ""
echo "GitHub → repo → Settings → Secrets and variables → Actions → New repository secret"

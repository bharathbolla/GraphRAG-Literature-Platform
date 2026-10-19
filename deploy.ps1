# ==============================================================================
# GraphRAG Literature Platform - Google Cloud Run Deployment Script (PowerShell)
# ==============================================================================
param(
    [string]$ProjectId = $(gcloud config get-value project 2>$null),
    [string]$Region = "us-central1",
    [string]$ServiceName = "graphrag-literature"
)

if (-not $ProjectId) {
    Write-Error "Google Cloud Project ID is required. Run 'gcloud config set project [PROJECT_ID]' or specify -ProjectId."
    exit 1
}

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "Deploying GraphRAG Literature Platform to Google Cloud Run" -ForegroundColor Cyan
Write-Host "Project ID:   $ProjectId"
Write-Host "Region:       $Region"
Write-Host "Service Name: $ServiceName"
Write-Host "========================================================================" -ForegroundColor Cyan

# 1. Enable services
Write-Host "1. Enabling required Google Cloud APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com aiplatform.googleapis.com --project $ProjectId

# 2. Build and deploy
Write-Host "2. Building and deploying container to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --source . `
    --project $ProjectId `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --min-instances 0 `
    --max-instances 10

Write-Host "========================================================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
$ServiceUrl = $(gcloud run services describe $ServiceName --platform managed --region $Region --project $ProjectId --format "value(status.url)")
Write-Host "Public Application URL: $ServiceUrl" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green

#!/usr/bin/env bash
# ==============================================================================
# GraphRAG Literature Platform - Google Cloud Run Deployment Script
# ==============================================================================
set -e

PROJECT_ID=${1:-$(gcloud config get-value project)}
REGION=${2:-"us-central1"}
SERVICE_NAME="graphrag-literature"

if [ -z "$PROJECT_ID" ]; then
  echo "Error: Google Cloud Project ID is required."
  echo "Usage: ./deploy.sh [PROJECT_ID] [REGION]"
  exit 1
fi

echo "========================================================================"
echo "Deploying GraphRAG Literature Platform to Google Cloud Run"
echo "Project ID:   $PROJECT_ID"
echo "Region:       $REGION"
echo "Service Name: $SERVICE_NAME"
echo "========================================================================"

# Enable required Google Cloud APIs
echo "1. Enabling required Google Cloud APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  --project "$PROJECT_ID"

# Build and deploy directly via Cloud Run source deploy
echo "2. Building and deploying container to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 10

echo "========================================================================"
echo "Deployment Complete!"
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --platform managed --region "$REGION" --project "$PROJECT_ID" --format "value(status.url)")
echo "Public Application URL: $SERVICE_URL"
echo "========================================================================"

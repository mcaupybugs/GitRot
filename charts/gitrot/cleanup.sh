#!/bin/bash

# GitRot Kubernetes Cleanup Script

set -e

echo "🧹 Cleaning up GitRot deployment..."

# Delete deployments and services
kubectl delete -f frontend-service.yaml -n gitrot --ignore-not-found=true
kubectl delete -f frontend-deployment.yaml -n gitrot --ignore-not-found=true
kubectl delete -f backend-service.yaml -n gitrot --ignore-not-found=true
kubectl delete -f backend-deployment.yaml -n gitrot --ignore-not-found=true

# Delete namespace (this removes everything)
kubectl delete -f namespace.yaml --ignore-not-found=true

echo "✅ Cleanup complete!"

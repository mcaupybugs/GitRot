#!/bin/bash

# GitRot Kubernetes Deployment Script
# Complete deployment with all dependencies

set -e

echo "🚀 Deploying GitRot to Kubernetes with all dependencies..."

# Check if ingress controller is installed
echo "🔍 Checking for ingress controller..."
if ! kubectl get pods -n ingress-nginx | grep -q "ingress-nginx-controller"; then
    echo "� Installing NGINX Ingress Controller..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
    
    echo "⏳ Waiting for ingress controller to be ready..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s
    
    echo "✅ Ingress controller installed and ready"
else
    echo "✅ Ingress controller already installed"
fi

# Create namespace
echo "📁 Creating namespace..."
kubectl apply -f namespace.yaml

# Deploy backend
echo "🔧 Deploying backend..."
kubectl apply -f backend-deployment.yaml -n gitrot
kubectl apply -f backend-service.yaml -n gitrot

# Deploy frontend  
echo "🎨 Deploying frontend..."
kubectl apply -f frontend-deployment.yaml -n gitrot
kubectl apply -f frontend-service.yaml -n gitrot

# Deploy ingress
echo "🌐 Deploying ingress..."
kubectl apply -f ingress.yaml -n gitrot

# Wait for deployments
echo "⏳ Waiting for deployments..."
kubectl wait --for=condition=available --timeout=300s deployment/gitrot-backend -n gitrot
kubectl wait --for=condition=available --timeout=300s deployment/gitrot-frontend -n gitrot

# Wait for ingress to get external IP
echo "⏳ Waiting for ingress to get external IP..."
for i in {1..30}; do
    INGRESS_IP=$(kubectl get ingress gitrot-ingress -n gitrot -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    if [ ! -z "$INGRESS_IP" ] && [ "$INGRESS_IP" != "null" ]; then
        break
    fi
    echo "Waiting for ingress IP... (attempt $i/30)"
    sleep 10
done

# Get service info
echo "✅ Deployment complete!"
echo ""
echo "📊 Service Status:"
kubectl get services -n gitrot
echo ""
echo "🏃 Pod Status:"
kubectl get pods -n gitrot
echo ""
echo "🌐 Ingress Status:"
kubectl get ingress -n gitrot
echo ""
echo "🌐 Access your application:"
INGRESS_IP=$(kubectl get ingress gitrot-ingress -n gitrot -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
if [ ! -z "$INGRESS_IP" ] && [ "$INGRESS_IP" != "null" ]; then
  echo "Application: http://$INGRESS_IP"
  echo "Backend API: http://$INGRESS_IP/api/"
else
  echo "Waiting for ingress IP... Check with: kubectl get ingress -n gitrot"
fi

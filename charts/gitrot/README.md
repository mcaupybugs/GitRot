# GitRot Kubernetes Deployment

Minimal Kubernetes deployment files for GitRot application.

## Files Structure

```
charts/gitrot/
├── namespace.yaml           # Creates gitrot namespace
├── backend-deployment.yaml  # Backend deployment
├── backend-service.yaml     # Backend service (ClusterIP)
├── frontend-deployment.yaml # Frontend deployment
├── frontend-service.yaml    # Frontend service (LoadBalancer)
├── deploy.sh               # Deployment script
├── cleanup.sh              # Cleanup script
└── README.md              # This file
```

## Prerequisites

- Kubernetes cluster running
- kubectl configured
- Docker images pushed to Docker Hub

## Quick Deployment

```bash
# Navigate to charts directory
cd charts/gitrot

# Deploy everything
./deploy.sh
```

## Manual Deployment

```bash
# Apply files individually
kubectl apply -f namespace.yaml
kubectl apply -f backend-deployment.yaml -n gitrot
kubectl apply -f backend-service.yaml -n gitrot
kubectl apply -f frontend-deployment.yaml -n gitrot
kubectl apply -f frontend-service.yaml -n gitrot
```

## Access the Application

### Option 1: Port Forwarding (Local development)

```bash
# Frontend
kubectl port-forward service/gitrot-frontend-service 3000:3000 -n gitrot

# Backend
kubectl port-forward service/gitrot-backend-service 8000:8000 -n gitrot
```

### Option 2: LoadBalancer (Cloud)

```bash
# Get external IP
kubectl get services -n gitrot

# Access via external IP
http://<EXTERNAL-IP>:3000
```

## Monitoring

```bash
# Check pods
kubectl get pods -n gitrot

# Check services
kubectl get services -n gitrot

# View logs
kubectl logs -f deployment/gitrot-backend -n gitrot
kubectl logs -f deployment/gitrot-frontend -n gitrot
```

## Cleanup

```bash
# Remove everything
./cleanup.sh

# Or manually
kubectl delete namespace gitrot
```

## Configuration

### Images Used

- **Backend**: `mcaupybugs/gitrot-backend:latest`
- **Frontend**: `mcaupybugs/gitrot-frontend:latest`

### Resources

- **Memory**: 256Mi request, 512Mi limit
- **CPU**: 250m request, 500m limit

### Health Checks

- **Backend**: `/health` endpoint
- **Frontend**: `/` endpoint

That's it! Minimal and ready to deploy! 🚀

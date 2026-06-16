# AI-Powered Kubernetes Troubleshooting Assistant

## Overview
This project is an AI-powered Kubernetes troubleshooting platform that analyzes pod failure logs and returns root cause, severity, evidence, and recommendations.

## Tech Stack
- FastAPI backend
- React frontend
- Docker
- Kubernetes
- Prometheus
- Grafana
- Alertmanager
- HPA
- NGINX Ingress
- TLS
- DockerHub
- GitHub Actions CI/CD

## Architecture

Developer pushes code to GitHub  
→ GitHub Actions builds Docker images  
→ Images are pushed to DockerHub  
→ Kubernetes pulls images  
→ Application runs behind Ingress  
→ Prometheus scrapes metrics  
→ Grafana visualizes dashboards  
→ Alertmanager sends alerts  

## Features
- AI-based Kubernetes log analysis
- Containerized frontend and backend
- Kubernetes deployment using Deployments and Services
- HTTPS access using Ingress and TLS
- Prometheus metrics endpoint
- Grafana dashboard
- Alertmanager email alerts
- Horizontal Pod Autoscaler
- CI/CD pipeline using GitHub Actions
- Docker images pushed to DockerHub

## Kubernetes Components
- Backend Deployment
- Backend Service
- Frontend Deployment
- Frontend Service
- Ingress
- HPA
- ServiceMonitor

## CI/CD
GitHub Actions automatically builds and pushes backend and frontend Docker images to DockerHub whenever code is pushed to the main branch.

## Monitoring and Alerting
Prometheus collects application and cluster metrics. Grafana is used for dashboards. Alertmanager sends email alerts when configured alert rules are triggered.

## Future Enhancements
- ArgoCD GitOps deployment
- Terraform-based AWS infrastructure
- AWS EKS deployment
- AWS Load Balancer Controller
- Route53 and ACM TLS
- External Secrets Operator with AWS Secrets Manager

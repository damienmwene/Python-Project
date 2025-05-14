# 🖥️ Uptime Monitor

A Python-based tool that monitors the availability of URLs and reports status in real-time. Fully automated using a CI/CD pipeline with GitHub Actions and deployed to AWS ECS.

## 🚀 Features

- Periodically checks the availability of given URLs
- Logs status (UP/DOWN) with timestamps
- Lightweight and containerized
- Built-in test cases
- Integrated Trivy security scan
- Automatically deployed on every push via GitHub Actions

## 🔧 Tech Stack

- Python
- Docker
- GitHub Actions
- AWS ECS (EC2 launch type)
- Trivy
- DockerHub

## 🛠️ CI/CD Workflow Overview

1. Run Python tests
2. Run Trivy vulnerability scan
3. Build Docker image
4. Push to DockerHub
5. Register new ECS task definition
6. Deploy to ECS cluster.

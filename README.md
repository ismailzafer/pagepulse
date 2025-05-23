# PagePulse: Cloud-Native PDF to Text Converter

A modern, cloud-native application that converts PDF files to searchable text using Google Cloud Platform services. Built with Vue.js, FastAPI, and GCP services.

![PagePulse Screenshot](screenshots/pagepulse.png)

---

## Features

- 📄 Upload and convert PDF files to searchable text
- ☁️ Cloud-native architecture using GCP services
- 🚀 Scalable processing with Kubernetes (GKE)
- 🖥️ Standalone VM for frontend hosting
- 📊 Real-time conversion status updates
- ⚡ Serverless PDF conversion with Cloud Functions
- 📦 Containerized workloads for portability
- 🧪 Performance testing with Locust

---

## Architecture

### Diagram

> (Insert your architecture diagram here, e.g. `screenshots/architecture.png`)

### Components

- **Frontend**: Vue.js 3 + Vuetify 3 web application (served via Nginx on a Compute Engine VM)
- **Backend API**: FastAPI application running on GKE (Google Kubernetes Engine)
- **Storage**: Google Cloud Storage for PDFs and text files
- **Processing**: Google Cloud Function for PDF-to-text conversion
- **Infrastructure**: Managed with Terraform (IaC)

### Flow

1. User uploads PDF via web UI
2. Backend validates and stores PDF in Cloud Storage
3. Backend triggers Cloud Function for conversion
4. Cloud Function converts PDF to text, saves result to Cloud Storage
5. Frontend polls backend for status
6. User downloads the converted text file

---

## Local Development

### Prerequisites

- Node.js 16+
- Python 3.8+
- Google Cloud SDK
- Docker
- kubectl
- Terraform

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Cloud Function Local Test

```bash
cd cloud-functions/pdf-converter
pip install -r requirements.txt
functions-framework --target=convert_pdf_to_text
```

---

## Infrastructure Deployment (Terraform)

1. **Configure GCP credentials** (do NOT commit your service account key!):
   - Place your service account key (e.g. `sa-key.json`) outside the repo and set the `GOOGLE_APPLICATION_CREDENTIALS` env variable.

2. **Deploy with Terraform:**

```bash
cd terraform
terraform init
terraform apply
```

This will create:
- GKE cluster
- Compute Engine VM
- Cloud Storage bucket
- Cloud Function
- Required IAM roles

---

## Backend Deployment (GKE)

```bash
# Build and push Docker image
docker build -t gcr.io/<your-project-id>/pagepulse-backend:latest .
docker push gcr.io/<your-project-id>/pagepulse-backend:latest

# Deploy to GKE
kubectl apply -f backend/deployment.yaml
kubectl apply -f backend/service.yaml
```

---

## Frontend Deployment (VM)

```bash
cd frontend
npm install
npm run build
# Zip and upload the dist/ folder to your VM
# On the VM, configure Nginx to serve the frontend
```

---

## Performance Testing (Locust)

```bash
pip install locust
locust -f locustfile.py
# Open http://localhost:8089 and configure the test
```

---

## Security & Best Practices

- **Never commit service account keys or secrets to the repository!**
- Add all secrets to `.gitignore`
- If a secret is accidentally committed, remove it from git history and revoke it in GCP

---

## Cost Analysis

> (Update with your actual GCP billing if available)

- GKE: ~$74.26/month
- Compute Engine VM: ~$6.11/month
- Cloud Functions: ~$1.85/month
- Storage: ~$5.46/month

---

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## Acknowledgments

- Built with Vue.js & GCP
- PDF processing using PyPDF2
- UI components from Vuetify
- Cloud architecture inspired by GCP best practices

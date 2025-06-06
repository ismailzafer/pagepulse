# PagePulse: Cloud-Native PDF to Text Converter

A modern, cloud-native application that converts PDF files to searchable text using Google Cloud Platform services. Built with Vue.js, FastAPI, and GCP services.

![PagePulse Screenshot](screenshots/pagepulse.png)

---

## Accessing the Project

You can access the PagePulse application at the following URL:

[http://34.51.186.94](http://34.51.186.94)

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

![Architecture Screenshot](screenshots/architecture.png)

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

## Detailed Setup and Deployment Steps

### 1. GCP Project and Service Account Setup

1. Create a new project in Google Cloud Console.
2. Enable the following APIs:
   - Compute Engine API
   - Kubernetes Engine API
   - Cloud Functions API
   - Cloud Storage API
3. Create a service account with `Owner` or necessary minimum permissions.
4. Download the service account key (JSON file). 
5. Set the key file path as an environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/sa-key.json"
   ```

### 2. Install Required Tools

- Google Cloud SDK (`gcloud`)
- Docker
- kubectl
- Terraform
- Node.js and npm
- Python 3.8+

### 3. Infrastructure Deployment with Terraform

1. Navigate to the `terraform/` directory:
   ```bash
   cd terraform
   terraform init
   terraform apply
   ```
2. Note the names and access details of the created resources (GKE, VM, Storage, Cloud Function) from the Terraform output.

### 4. Backend (FastAPI) Docker Image Build and Push to GCR

1. In the project root directory:
   ```bash
   docker build -t gcr.io/<project-id>/pagepulse-backend:latest .
   docker push gcr.io/<project-id>/pagepulse-backend:latest
   ```
2. Deploy to GKE:
   ```bash
   kubectl apply -f backend/deployment.yaml
   kubectl apply -f backend/service.yaml
   kubectl apply -f backend/hpa.yaml
   ```
3. Get the external IP:
   ```bash
   kubectl get svc
   ```
   Use this IP as the API address in the frontend `.env` file.

### 5. Frontend (Vue.js) Build and VM Deployment

1. In the frontend directory:
   ```bash
   cd frontend
   npm install
   npm run build
   ```
2. Zip the `dist/` folder and upload it to the VM using SCP:
   ```bash
   scp -i <ssh-key> -r dist/ <user>@<vm-ip>:/var/www/pagepulse
   ```
3. Configure Nginx on the VM:
   - Set the root directory in `/etc/nginx/sites-available/default` to `/var/www/pagepulse`.
   - Restart Nginx:
     ```bash
     sudo systemctl restart nginx
     ```

### 6. Cloud Function Deployment (Detailed)

1. Navigate to the Cloud Function code directory:
   ```bash
   cd cloud-functions/pdf-converter
   ```
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Deploy the Cloud Function:
   ```bash
   gcloud functions deploy convert_pdf_to_text \
     --runtime python310 \
     --trigger-http \
     --allow-unauthenticated \
     --entry-point convert_pdf_to_text \
     --region <region> \
     --project <project-id>
   ```
   - Ensure the `--entry-point` matches the function name in your code.
   - Use the URL provided after deployment in your backend settings.

#### Notes:
- The Cloud Function is triggered by Google Cloud Storage events. Use `--trigger-resource` and `--trigger-event` parameters to set it up as a storage-triggered function. Specify the storage bucket as `pdf-bucket`.
- Ensure the service account has necessary IAM permissions (Cloud Functions Invoker, Storage Object Admin, etc.).

### 7. Cloud Storage Setup

1. Create a Cloud Storage bucket:
   ```bash
   gsutil mb gs://pdf-bucket
   ```
2. Set the appropriate permissions for the bucket:
   ```bash
   gsutil iam ch allUsers:objectViewer gs://pdf-bucket
   ```
3. Ensure the Cloud Function has access to the bucket by setting the necessary IAM roles.

### 8. Common Settings and Tips

- **CORS:** Check CORS settings in the backend and Cloud Function.
- **Firewall:** Ensure necessary ports (80, 443, 8000, etc.) are open for GKE and VM.
- **Environment Variables:** Update API URLs, GCS bucket names, etc., in `.env` files.
- **Error Handling:** Refer to GCP documentation and console for quota issues, IAM permissions, and region compatibility.

### 9. Performance Testing (Locust)

1. Install Locust:
   ```bash
   pip install locust
   ```
2. Start the test:
   ```bash
   locust -f locustfile.py
   ```
3. Configure test parameters via the web interface (http://localhost:8089) and start the test.
4. Save results and graphs in the `screenshots/` directory.

---




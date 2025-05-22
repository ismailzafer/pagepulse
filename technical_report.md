# PagePulse: Cloud-Native PDF to Text Converter - Technical Report

## 1. Introduction

This report documents the design, implementation, and evaluation of PagePulse, a cloud-native application built on Google Cloud Platform (GCP). The project integrates containerized workloads, virtual machines, and serverless functions to provide a scalable and efficient PDF-to-text conversion service.

## 2. Cloud Architecture

### 2.1 Architecture Diagram

[Insert architecture diagram here]

### 2.2 Components

- **Frontend:** Vue.js 3 + Vuetify 3 web application, deployed on a GCP VM and served via Nginx.
- **Backend API:** FastAPI application, containerized and deployed on Google Kubernetes Engine (GKE).
- **Storage:** 
  - Local storage: PDFs and text files are stored in `backend/uploads/` and `backend/conversions/`.
  - Cloud Storage: Optional storage in a GCS bucket (`pagepulse-pdf-bucket`).
- **Processing:** Cloud Function (`pdf-converter`) for PDF-to-text conversion.
- **Messaging:** Cloud Pub/Sub for asynchronous communication.
- **Infrastructure:** Terraform for Infrastructure as Code (IaC).

### 2.3 Interaction Flow

1. User uploads a PDF via the web UI.
2. Backend validates and stores the PDF locally.
3. Pub/Sub message triggers the conversion process.
4. Cloud Function converts the PDF to text and optionally saves it to GCS.
5. Frontend polls for completion status.
6. User downloads the converted text file.

## 3. Deployment Process

### 3.1 Manual Deployment

1. **Google Cloud Setup:**
   - Create a new GCP project.
   - Enable required APIs (Cloud Storage, Cloud Functions, Pub/Sub, Kubernetes Engine).
   - Create service accounts and download credentials.

2. **Backend Deployment:**
   - Build and push the Docker image to Google Container Registry (GCR).
   - Deploy to GKE using Kubernetes manifests (`deployment.yaml`, `service.yaml`).

3. **Frontend Deployment:**
   - Build the Vue.js app and upload the `dist` folder to the VM.
   - Configure Nginx to serve the frontend.

4. **Cloud Function Deployment:**
   - Deploy the Cloud Function using `gcloud` or Terraform.

### 3.2 Terraform Deployment

1. Navigate to the `terraform` directory.
2. Initialize Terraform:
   ```bash
   terraform init
   ```
3. Apply the Terraform configuration:
   ```bash
   terraform apply
   ```
   This creates:
   - VPC and subnet
   - Cloud Storage bucket
   - Pub/Sub topic
   - Cloud Function
   - VM instance

## 4. Performance Evaluation

### 4.1 Locust Test Design

- **Endpoints Tested:**
  - `/upload/`: Upload PDF files.
  - `/status/{file_id}`: Check conversion status.
- **Test Parameters:**
  - Number of users: 10
  - Spawn rate: 1
  - Host: `http://<backend-external-ip>`

### 4.2 Metrics Collected

- Request latency
- Throughput (requests per second)
- Resource usage (CPU, memory)
- Error rates under load

### 4.3 Results

[Insert Locust test results, charts, and screenshots here]

## 5. Cost Analysis

### 5.1 Resource Usage and Cost Breakdown

- GKE: $74.26 (1 zonal cluster with e2-small node)
- Compute Engine VM: $6.11 (e2-micro instance)
- Cloud Functions: $1.85 (512 MiB memory, 1M requests/month)
- Storage: $5.46 (10 GiB disk)

### 5.2 Budget Compliance

[Insert GCP billing screenshots and discussion here]

## 6. Discussion

### 6.1 Challenges and Lessons Learned

- Challenges encountered during deployment and integration.
- Lessons learned and best practices applied.

### 6.2 Future Improvements

- Potential enhancements and optimizations.

## 7. Conclusion

PagePulse successfully demonstrates a cloud-native architecture using GCP services. The project meets the requirements for scalability, efficiency, and cost-effectiveness.

## 8. References

- GCP Documentation
- Vue.js and FastAPI Documentation
- Terraform Documentation

## 9. Appendix

- Additional screenshots, logs, or code snippets. 
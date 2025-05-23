terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "container.googleapis.com",
    "cloudfunctions.googleapis.com",
    "storage.googleapis.com",
    "compute.googleapis.com"
  ])
  
  project = var.project_id
  service = each.key

  disable_dependent_services = false
  disable_on_destroy        = false
}

# Create VPC network
resource "google_compute_network" "vpc" {
  name                    = "pagepulse-vpc"
  auto_create_subnetworks = false
}

# Create subnet
resource "google_compute_subnetwork" "subnet" {
  name          = "pagepulse-subnet"
  ip_cidr_range = "10.0.0.0/24"
  network       = google_compute_network.vpc.name
  region        = var.region
}

# Create Cloud Storage bucket
resource "google_storage_bucket" "pdf_bucket" {
  name          = "pagepulse-pdf-bucket"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true
}

# Create Cloud Function
resource "google_cloudfunctions_function" "pdf_converter" {
  name        = "pdf-converter"
  description = "Function to convert PDFs to text"
  runtime     = "python39"

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.pdf_bucket.name
  source_archive_object = google_storage_bucket_object.function_zip.name
  trigger_http          = true
  entry_point           = "convert_pdf_to_text"

  environment_variables = {
    BUCKET_NAME = google_storage_bucket.pdf_bucket.name
  }
}

# Create VM instance
resource "google_compute_instance" "app_server" {
  name         = "pagepulse-app-server"
  machine_type = "e2-medium"
  zone         = "europe-north2-a"

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
    }
  }

  network_interface {
    network    = google_compute_network.vpc.name
    subnetwork = google_compute_subnetwork.subnet.name
    access_config {
      // Ephemeral public IP
    }
  }
}

resource "google_storage_bucket_object" "function_zip" {
  name   = "function.zip"
  bucket = google_storage_bucket.pdf_bucket.name
  source = "../cloud-functions/function.zip"
} 
# Configure the Google Cloud provider
provider "google" {
  project = var.project_id
  region  = var.region
}

# -----------------
# API Enablement
# -----------------
# Best practice: ensure necessary APIs are enabled
resource "google_project_service" "dataflow" {
  service = "dataflow.googleapis.com"
}

resource "google_project_service" "pubsub" {
  service = "pubsub.googleapis.com"
}

resource "google_project_service" "bigquery" {
  service = "bigquery.googleapis.com"
}


# -----------------
# GCS Bucket for Dataflow
# -----------------
resource "google_storage_bucket" "dataflow_bucket" {
  name          = var.gcs_bucket_name
  location      = var.region
  force_destroy = true # Useful for dev environments

  uniform_bucket_level_access = true

  depends_on = [google_project_service.dataflow]
}


# -----------------
# Pub/Sub for Data Ingestion
# -----------------
# Topic for the source application to publish messages to
resource "google_pubsub_topic" "source_topic" {
  name = var.pubsub_topic_name
  depends_on = [google_project_service.pubsub]
}

# Subscription for the Dataflow job to read messages from
resource "google_pubsub_subscription" "dataflow_subscription" {
  name  = "${var.pubsub_topic_name}-sub"
  topic = google_pubsub_topic.source_topic.name

  # Retain acknowledged messages for 1 day
  message_retention_duration = "86400s"
  # Give 20 seconds for Dataflow to process a message
  ack_deadline_seconds = 20
}


# -----------------
# BigQuery for Data Storage
# -----------------
# Dataset to hold our tables
resource "google_bigquery_dataset" "analytics_dataset" {
  dataset_id = var.bigquery_dataset_name
  location   = var.region
  depends_on = [google_project_service.bigquery]
}

# Table with the schema matching the Dataflow job's output
resource "google_bigquery_table" "summary_table" {
  dataset_id = google_bigquery_dataset.analytics_dataset.dataset_id
  table_id   = var.bigquery_table_name
  deletion_protection = false # Set to true for production to prevent accidental deletion
  # The schema for the aggregated player data
  schema = jsonencode([
    {
      "name": "player_id",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
      "name": "room_id",
      "type": "STRING",
      "mode": "REQUIRED"
    },
    {
      "name": "player_name",
      "type": "STRING",
      "mode": "NULLABLE"
    },
    {
      "name": "total_gifts",
      "type": "INTEGER",
      "mode": "NULLABLE"
    },
    {
      "name": "total_game_currency",
      "type": "INTEGER",
      "mode": "NULLABLE"
    },
    {
      "name": "total_diamonds",
      "type": "INTEGER",
      "mode": "NULLABLE"
    },
    {
      "name": "total_usd",
      "type": "FLOAT",
      "mode": "NULLABLE"
    },
    {
      "name": "window_timestamp",
      "type": "TIMESTAMP",
      "mode": "REQUIRED"
    }
  ])
}
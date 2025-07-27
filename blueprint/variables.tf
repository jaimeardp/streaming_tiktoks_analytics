variable "project_id" {
  description = "The GCP project ID to deploy resources to."
  type        = string
}

variable "region" {
  description = "The GCP region for the resources."
  type        = string
  default     = "us-central1"
}

variable "gcs_bucket_name" {
  description = "The name for the GCS bucket for Dataflow staging."
  type        = string
}

variable "pubsub_topic_name" {
  description = "The name for the Pub/Sub topic."
  type        = string
  default     = "tiktok-gift-events"
}

variable "bigquery_dataset_name" {
  description = "The name for the BigQuery dataset."
  type        = string
  default     = "tiktok_analytics_raw"
}

variable "bigquery_table_name" {
  description = "The name for the BigQuery table for aggregated results."
  type        = string
  default     = "player_summary"
}


//  Big table variables


variable "cluster_zone" {
  description = "The GCP zone for the Bigtable cluster."
  type        = string
  default     = "us-central1-b"
}

variable "instance_name" {
  description = "The desired name for the Bigtable instance."
  type        = string
  default     = "tiktok-analytics-ins"
}

variable "table_name" {
  description = "The desired name for the Bigtable table."
  type        = string
  default     = "live-events"
}
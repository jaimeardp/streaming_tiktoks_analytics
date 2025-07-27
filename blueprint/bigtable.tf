# Ensures the Bigtable API is enabled on your project
resource "google_project_service" "bigtable" {
  project = var.project_id
  service = "bigtable.googleapis.com"
}

# Creates the Bigtable Instance which holds your clusters
resource "google_bigtable_instance" "api_instance" {
  name    = var.instance_name
  project = var.project_id
  # You can add more clusters for replication and higher availability
  cluster {
    cluster_id   = "${var.instance_name}-cluster"
    zone         = var.cluster_zone
    num_nodes    = 1 # Start with 1 and enable autoscaling or increase as needed
    storage_type = "SSD"
  }

  deletion_protection = false # Set to true for production environments
  depends_on = [
    google_project_service.bigtable
  ]
}

# Creates the table that will store your event data
resource "google_bigtable_table" "event_table" {
  name          = var.table_name
  project       = var.project_id
  instance_name = google_bigtable_instance.api_instance.name

  # Defines the column family. All related data will be stored under here.
  column_family {
    family = "gift_data"
  }
}
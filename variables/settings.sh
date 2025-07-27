# Set your project and bucket details
export PROJECT_ID="you-project-id"
export BUCKET_NAME="buckets-discovery-tiktok-analytics"
export REGION="us-central1" # Or your preferred region

# Set the Pub/Sub subscription and BigQuery table details
export INPUT_SUBSCRIPTION="projects/${PROJECT_ID}/subscriptions/tiktok-gift-events-sub"
export OUTPUT_TABLE="${PROJECT_ID}:tiktok_analytics_raw.player_summary"
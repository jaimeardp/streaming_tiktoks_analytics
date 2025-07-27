





gcloud builds submit --tag us-central1-docker.pkg.dev/you-project-id/tiktok-repository/tiktok-api

gcloud run deploy tiktok-api \
  --image us-central1-docker.pkg.dev/you-project-id/tiktok-repository/tiktok-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=you-project-id,BIGTABLE_INSTANCE_ID=tiktok-analytics-ins,BIGTABLE_TABLE_ID=live-events


python streaming_job.py \
    --runner=DataflowRunner \
    --project=you-project-id \
    --region=us-central1 \
    --temp_location=gs://buckets-discovery-tiktok-analytics/temp \
    --staging_location=gs://buckets-discovery-tiktok-analytics/staging \
    --input_subscription=projects/you-project-id/subscriptions/tiktok-gift-events-sub \
    --output_table=you-project-id:tiktok_analytics_raw.player_summary \
    --bigtable_project_id=you-project-id \
    --bigtable_instance_id=tiktok-analytics-ins \
    --bigtable_table_id=live-events

python streaming_job.py --runner=DataflowRunner --project=you-project-id --region=us-central1 --temp_location=gs://buckets-discovery-tiktok-analytics/temp --staging_location=gs://buckets-discovery-tiktok-analytics/staging --input_subscription=projects/you-project-id/subscriptions/tiktok-gift-events-sub --output_table=you-project-id:tiktok_analytics_raw.player_summary --bigtable_project_id=you-project-id --bigtable_instance_id=tiktok-analytics-ins --bigtable_table_id=live-events

gcloud artifacts repositories create tiktok-repository --repository-format=docker --region=us-central1 --description="Repository for TikTok API images"d

gcloud builds submit --tag us-central1-docker.pkg.dev/you-project-id/tiktok-repository/tiktok-api

gcloud run deploy tiktok-api  --image us-central1-docker.pkg.dev/you-project-id/tiktok-repository/tiktok-api  --platform managed   --region us-central1  --allow-unauthenticated   --set-env-vars GCP_PROJECT_ID=you-project-id,BIGTABLE_INSTANCE_ID=tiktok-analytics-ins,BIGTABLE_TABLE_ID=live-events


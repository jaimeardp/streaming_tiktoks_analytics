CREATE OR REPLACE VIEW `oceanic-student-465214-j2.tiktok_analytics_delivery.vw_hourly_performance` AS
SELECT
  -- Extracts the hour from the timestamp and formats it for readability (e.g., "14:00")
  FORMAT_TIMESTAMP('%H:00', TIMESTAMP_TRUNC(window_timestamp, HOUR)) AS hour_of_day,
  SUM(total_usd) AS total_revenue_usd,
  SUM(total_gifts) AS total_gift_count
FROM
  -- IMPORTANT: Replace with the full path to your aggregated summary table
  `oceanic-student-465214-j2.tiktok_analytics_enriched.vw_business_player_summary`
WHERE
  -- Filter for data from the last 24 hours
  window_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY
  hour_of_day
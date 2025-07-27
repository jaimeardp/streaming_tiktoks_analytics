CREATE OR REPLACE VIEW `oceanic-student-465214-j2.tiktok_analytics_delivery.vw_top_streams_by_revenue` AS
SELECT
  room_id,
  SUM(total_usd) AS total_revenue_usd
FROM
  -- IMPORTANT: Replace with the full path to your aggregated summary table
  `oceanic-student-465214-j2.tiktok_analytics_enriched.vw_business_player_summary`
WHERE
  -- Filter for data from the last 24 hours
  window_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY
  room_id
ORDER BY
  total_revenue_usd DESC
LIMIT 10
CREATE OR REPLACE VIEW `oceanic-student-465214-j2.tiktok_analytics_delivery.vw_kpi_scoreboard` AS

SELECT
  SUM(total_usd) AS total_revenue_today,
  SUM(total_gifts) AS total_gifts_today,
  COUNT(DISTINCT player_id) AS unique_players_today,
  COUNT(DISTINCT room_id) AS unique_rooms_today
FROM
  -- IMPORTANT: Replace with the full path to your aggregated summary table
  `oceanic-student-465214-j2.tiktok_analytics_raw.player_summary`
WHERE
  -- Filter for data from the last 24 hours
  window_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
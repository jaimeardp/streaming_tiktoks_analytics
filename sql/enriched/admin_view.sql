-- deprecated: This view is no longer used and will be removed in future versions.
CREATE OR REPLACE VIEW `oceanic-student-465214-j2.tiktok_analytics_enriched.vw_admin_player_summary` AS
SELECT
  -- Show all data including personal identifiers
  player_id,
  player_name,
  total_usd,
  total_gifts,
  total_game_currency,
  total_diamonds,
  room_id,
  window_timestamp,
  
  -- Add admin-specific fields
  CONCAT('Player: ', player_name, ' (ID: ', player_id, ')') as full_identifier,
  

FROM `oceanic-student-465214-j2.tiktok_analytics_raw.player_summary`;
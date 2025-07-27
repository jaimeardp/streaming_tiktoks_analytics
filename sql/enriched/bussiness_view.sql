CREATE OR REPLACE VIEW `oceanic-student-465214-j2.tiktok_analytics_enriched.vw_bussiness_player_summary` AS
SELECT
  -- Hash personal identifiers instead of NULL
  TO_BASE64(SHA256(player_id)) as player_id_hash,
  CONCAT(SUBSTR(player_name, 1, 3), '***') as player_name_masked,
  
  -- Show all business data
  total_usd,
  total_gifts,
  total_game_currency,
  total_diamonds,
  room_id,
  window_timestamp


FROM `oceanic-student-465214-j2.tiktok_analytics_raw.player_summary`;
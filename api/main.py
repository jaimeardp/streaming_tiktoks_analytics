import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS
from google.cloud.bigtable import Client


# --- Configuration ---
GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
BIGTABLE_INSTANCE_ID = os.environ.get('BIGTABLE_INSTANCE_ID')
BIGTABLE_TABLE_ID = os.environ.get('BIGTABLE_TABLE_ID')
COLUMN_FAMILY_ID = "gift_data"

# NEW: Conversion rate for diamonds to USD
DIAMOND_TO_USD_RATE = 0.005

# --- Initialization ---
app = Flask(__name__)
CORS(app)
bigtable_client = Client(project=GCP_PROJECT_ID)
instance = bigtable_client.instance(BIGTABLE_INSTANCE_ID)
table = instance.table(BIGTABLE_TABLE_ID)

# --- Helper Functions ---
def get_reversed_timestamp_micros(dt_object: datetime) -> int:
    """Calculates the reversed timestamp from a datetime object."""
    timestamp_micros = int(dt_object.timestamp() * 1_000_000)
    return (2**63 - 1) - timestamp_micros

# --- API Endpoints ---
@app.route('/streams/<string:room_id>/feed', methods=['GET'])
def get_live_feed(room_id):
    """Gets the latest N gifts for a given stream with a richer payload including USD value."""
    limit = int(request.args.get('limit', 20))
    start_key = f"{room_id}#".encode('utf-8')
    rows = table.read_rows(start_key=start_key, limit=limit)

    feed = []
    for row in rows:
        cells = row.cells.get(COLUMN_FAMILY_ID, {})
        # CHANGED: Get diamond value to calculate USD equivalent
        diamond_value = int(cells.get(b'originalGift.diamond_value', [b'0'])[0].value)
        usd_value = diamond_value * DIAMOND_TO_USD_RATE
        
        feed.append({
            'playerId': cells.get(b'playerId', [b''])[0].value.decode('utf-8'),
            'playerName': cells.get(b'playerName', [b''])[0].value.decode('utf-8'),
            'giftValue': int(cells.get(b'giftValue', [b'0'])[0].value),
            'giftType': cells.get(b'giftType', [b''])[0].value.decode('utf-8'),
            'originalGiftName': cells.get(b'originalGift.name', [b''])[0].value.decode('utf-8'),
            'usd_value': round(usd_value, 4), # NEW: Add USD value to each gift
            'timestamp': row.cells[COLUMN_FAMILY_ID][b'timestamp'][0].timestamp.isoformat()
        })
    return jsonify(feed)


@app.route('/streams/<string:room_id>/leaderboard', methods=['GET'])
def get_leaderboard(room_id):
    """Calculates a leaderboard, sorted by total USD value."""
    minutes = int(request.args.get('minutes', 5))
    filter_type = request.args.get('type')

    now = datetime.now(timezone.utc)
    start_time = now - timedelta(minutes=minutes)
    start_key = f"{room_id}#{get_reversed_timestamp_micros(now)}".encode('utf-8')
    end_key = f"{room_id}#{get_reversed_timestamp_micros(start_time)}".encode('utf-8')
    rows = table.read_rows(start_key=start_key, end_key=end_key)

    scores = defaultdict(int)
    usd_scores = defaultdict(float)
    player_names = {}

    for row in rows:
        cells = row.cells.get(COLUMN_FAMILY_ID, {})
        current_type = cells.get(b'giftType', [b''])[0].value.decode('utf-8')

        if filter_type and current_type != filter_type:
            continue

        player_id = cells.get(b'playerId', [b''])[0].value.decode('utf-8')
        gift_value = int(cells.get(b'giftValue', [b'0'])[0].value)
        diamond_value = int(cells.get(b'originalGift.diamond_value', [b'0'])[0].value)

        # Aggregate both scores
        usd_scores[player_id] += diamond_value * DIAMOND_TO_USD_RATE
        scores[player_id] += gift_value
        
        if player_id not in player_names:
            player_names[player_id] = cells.get(b'playerName', [b''])[0].value.decode('utf-8')
            
    # CHANGED: Sort by the usd_scores dictionary instead of the game currency scores.
    sorted_scores_by_usd = sorted(usd_scores.items(), key=lambda item: item[1], reverse=True)
    
    # CHANGED: Build the final list from the USD-sorted list.
    leaderboard_result = [
        {
            'rank': i + 1,
            'playerId': pid,
            'playerName': player_names.get(pid, ''),
            'totalValue': scores.get(pid, 0), # Get corresponding game currency value
            'totalUSD': round(usd_score, 4)   # This is the value we sorted by
        }
        for i, (pid, usd_score) in enumerate(sorted_scores_by_usd)
    ]

    return jsonify({
        # CHANGED: Clarify that the ranking is now based on USD
        "ranking_by": "totalUSD",
        "leaderboard": leaderboard_result[:10]
    })
@app.route('/streams/<string:room_id>/summary', methods=['GET'])
def get_summary(room_id):
    """Provides a summary of all currency totals and a grand total in USD."""
    minutes = int(request.args.get('minutes', 5))
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(minutes=minutes)

    start_key = f"{room_id}#{get_reversed_timestamp_micros(now)}".encode('utf-8')
    end_key = f"{room_id}#{get_reversed_timestamp_micros(start_time)}".encode('utf-8')
    rows = table.read_rows(start_key=start_key, end_key=end_key)

    currency_totals = defaultdict(int)
    grand_total_usd = 0.0 # NEW: Initialize USD total

    for row in rows:
        cells = row.cells.get(COLUMN_FAMILY_ID, {})
        gift_type = cells.get(b'giftType', [b''])[0].value.decode('utf-8')
        gift_value = int(cells.get(b'giftValue', [b'0'])[0].value)

        # NEW: Calculate and aggregate total USD value
        diamond_value = int(cells.get(b'originalGift.diamond_value', [b'0'])[0].value)
        grand_total_usd += diamond_value * DIAMOND_TO_USD_RATE

        if gift_type:
            currency_totals[gift_type] += gift_value

    return jsonify({
        "time_window_minutes": minutes,
        "currency_totals": currency_totals,
        "grand_total_usd": round(grand_total_usd, 4) # NEW: Add grand total USD to summary
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.transforms import window
from apache_beam.io.gcp.bigquery import WriteToBigQuery, BigQueryDisposition
from apache_beam.io import ReadFromPubSub

from google.cloud import bigtable
from google.cloud.bigtable.row import DirectRow

import json
import logging
from datetime import datetime

# === DoFn: Parse JSON from PubSub ===
class ParseJsonDoFn(beam.DoFn):
    def process(self, element):
        try:
            yield json.loads(element.decode("utf-8"))
        except Exception as e:
            logging.error(f"[ParseJson] Error: {e} | Element: {element}")


# === DoFn: Create Bigtable Rows ===
class CreateBigtableRow(beam.DoFn):
    def get_reversed_timestamp_micros(self, dt: datetime) -> int:
        return (2**63 - 1) - int(dt.timestamp() * 1_000_000)

    def process(self, element):
        try:
            ts_str = element.get('timestamp')
            if not ts_str:
                return
            dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))

            room_id = element.get('originalGift', {}).get('room_id', 'unknown_room')
            reversed_ts = self.get_reversed_timestamp_micros(dt)
            row_key = f"{room_id}#{reversed_ts}".encode('utf-8')

            row_obj = DirectRow(row_key=row_key)

            for k, v in element.items():
                if isinstance(v, dict):
                    for sub_k, sub_v in v.items():
                        row_obj.set_cell('gift_data', f"{k}.{sub_k}".encode(), str(sub_v).encode(), timestamp=dt)
                elif v is not None:
                    row_obj.set_cell('gift_data', k.encode(), str(v).encode(), timestamp=dt)

            yield row_obj
        except Exception as e:
            logging.error(f"[CreateRow] Error: {e} | Element: {element}")


# === DoFn: Write to Bigtable (API native) ===
class WriteToBigtableFn(beam.DoFn):
    def __init__(self, project_id, instance_id, table_id):
        self.project_id = project_id
        self.instance_id = instance_id
        self.table_id = table_id

    def setup(self):
        self.client = bigtable.Client(project=self.project_id, admin=True)
        self.instance = self.client.instance(self.instance_id)
        self.table = self.instance.table(self.table_id)

    def process(self, row_obj):
        try:
            self.table.mutate_rows([row_obj])
        except Exception as e:
            logging.error(f"[WriteBT] Error writing row: {e}")


# === DoFn: Aggregate for BigQuery ===
class AggregateByPlayerAndRoom(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam):
        (player_id, room_id), gifts = element

        if not gifts:
            return

        player_name = gifts[0].get('playerName', 'Unknown')
        total_gifts = len(gifts)
        total_game_currency = sum(g.get('giftValue', 0) for g in gifts)
        total_diamonds = sum(g.get('originalGift', {}).get('diamond_value', 0) for g in gifts)
        window_end = window.end.to_utc_datetime().isoformat()

        yield {
            "player_id": player_id,
            "room_id": room_id,
            "player_name": player_name,
            "total_gifts": total_gifts,
            "total_game_currency": total_game_currency,
            "total_diamonds": total_diamonds,
            "total_usd": total_diamonds * 0.005,
            "window_timestamp": window_end,
        }



# === Custom Options ===
class CustomOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument('--input_subscription', required=True)
        parser.add_argument('--output_table', required=True)
        parser.add_argument('--bigtable_project_id', required=True)
        parser.add_argument('--bigtable_instance_id', required=True)
        parser.add_argument('--bigtable_table_id', required=True)


# === Run pipeline ===
def run():
    options = PipelineOptions(streaming=True)
    custom = options.view_as(CustomOptions)
    std_opts = options.view_as(StandardOptions)
    std_opts.streaming = True

    bq_schema = {
        "fields": [
            {"name": "player_id", "type": "STRING", "mode": "REQUIRED"},
            {"name": "room_id", "type": "STRING", "mode": "REQUIRED"},
            {"name": "player_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "total_gifts", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "total_game_currency", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "total_diamonds", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "window_timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
        ]
    }

    with beam.Pipeline(options=options) as p:
        parsed = (
            p
            | 'Read PubSub' >> ReadFromPubSub(subscription=custom.input_subscription)
            | 'Parse JSON' >> beam.ParDo(ParseJsonDoFn())
        )

        # --- Bigtable branch ---
        (
            parsed
            | 'To BT Row' >> beam.ParDo(CreateBigtableRow())
            | 'Write to Bigtable' >> beam.ParDo(WriteToBigtableFn(
                project_id=custom.bigtable_project_id,
                instance_id=custom.bigtable_instance_id,
                table_id=custom.bigtable_table_id
            ))
        )

        # --- BigQuery branch ---
        (
            parsed
            | 'Key by Player and Room' >> beam.Map(
                lambda x: ((x.get("playerId", "unknown"), x.get("originalGift", {}).get("room_id", "unknown")), x)
            )
            | 'Window 20s' >> beam.WindowInto(window.FixedWindows(20))
            | 'Group by Player and Room' >> beam.GroupByKey()
            | 'Aggregate Gifts' >> beam.ParDo(AggregateByPlayerAndRoom())
            | 'Write to BQ' >> WriteToBigQuery(
                table=custom.output_table,
                schema=bq_schema,
                create_disposition=BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=BigQueryDisposition.WRITE_APPEND
            )
        )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()

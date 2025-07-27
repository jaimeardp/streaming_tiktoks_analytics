import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms import window
import os
import json
import logging
import datetime

class ParseJsonDoFn(beam.DoFn):
    """Parses the JSON string from Pub/Sub into a Python dictionary."""
    def process(self, element: bytes):
        try:
            # Decode bytes to string and then load JSON
            yield json.loads(element.decode('utf-8'))
        except json.JSONDecodeError as e:
            logging.error("Failed to decode JSON: %s for element: %s", e, element)

class AggregateGiftsDoFn(beam.DoFn):
    """
    Aggregates the grouped gifts for a player within a specific window.
    Outputs a single dictionary ready for BigQuery.
    """
    def process(self, element, window=beam.DoFn.WindowParam):
        player_id, gifts = element
        
        # We need to grab player_name from the first gift event
        # In a real-world scenario, you might have a static data source for player names
        player_name = gifts[0].get('playerName', 'Unknown')
        
        total_gifts = len(gifts)
        total_game_currency = sum(g.get('giftValue', 0) for g in gifts)
        total_diamonds = sum(g['originalGift'].get('diamond_value', 0) for g in gifts)
        
        # Get the end of the window as a timestamp
        window_end = window.end.to_utc_datetime().isoformat()
        
        yield {
            "player_id": player_id,
            "player_name": player_name,
            "total_gifts": total_gifts,
            "total_game_currency": total_game_currency,
            "total_diamonds": total_diamonds,
            "window_timestamp": window_end,
        }

def run():
    """Defines and runs the Dataflow streaming pipeline."""
    
    # --- 1. Pipeline and BigQuery Setup ---
    pipeline_options = PipelineOptions(streaming=True)
    
    # Define the BigQuery table schema
    table_schema = {
        'fields': [
            {'name': 'player_id', 'type': 'STRING', 'mode': 'REQUIRED'},
            {'name': 'player_name', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'total_gifts', 'type': 'INTEGER', 'mode': 'NULLABLE'},
            {'name': 'total_game_currency', 'type': 'INTEGER', 'mode': 'NULLABLE'},
            {'name': 'total_diamonds', 'type': 'INTEGER', 'mode': 'NULLABLE'},
            {'name': 'window_timestamp', 'type': 'TIMESTAMP', 'mode': 'REQUIRED'},
        ]
    }
    
    # Custom pipeline arguments
    class CustomPipelineOptions(PipelineOptions):
        @classmethod
        def _add_argparse_args(cls, parser):
            parser.add_argument(
                '--input_subscription',
                required=True,
                help='Pub/Sub subscription to read from, in format projects/PROJECT_ID/subscriptions/SUBSCRIPTION_ID'
            )
            parser.add_argument(
                '--output_table',
                required=True,
                help='BigQuery table to write to, in format PROJECT_ID:DATASET_ID.TABLE_ID'
            )

    options = pipeline_options.view_as(CustomPipelineOptions)

    # --- 2. Build and Run the Pipeline ---
    with beam.Pipeline(options=options) as p:
        # Read from Pub/Sub -> Parse -> Key -> Window -> Group -> Aggregate -> Write to BQ
        (
            p
            | 'ReadFromPubSub' >> beam.io.ReadFromPubSub(
                subscription=options.input_subscription
            )
            | 'ParseJSON' >> beam.ParDo(ParseJsonDoFn())
            
            # Key the elements by player_id for grouping
            | 'KeyByPlayerId' >> beam.Map(lambda elem: (elem['playerId'], elem))
            # This is the core requirement: Apply a 20-second fixed window
            | 'Apply20sWindow' >> beam.WindowInto(window.FixedWindows(20))

            # Group all elements for each key (player_id) within the window
            | 'GroupByPlayer' >> beam.GroupByKey()
            
            # Aggregate the grouped gifts into a single record per player per window
            | 'AggregateGifts' >> beam.ParDo(AggregateGiftsDoFn())

            # Write the aggregated records to BigQuery
            | 'WriteToBigQuery' >> beam.io.WriteToBigQuery(
                table=options.output_table,
                schema=table_schema,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
            )
        )

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
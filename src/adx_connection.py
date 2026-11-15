import tomllib
from pathlib import Path

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table


# Load configuration
project_root = Path(__file__).resolve().parent.parent

with open(project_root / "config.toml", "rb") as file:
    config = tomllib.load(file)

cluster = config["adx"]["cluster"]
database = config["adx"]["database"]


# Establish ADX connection
kcsb = KustoConnectionStringBuilder.with_interactive_login(cluster)
client = KustoClient(kcsb)


# Helper function
def run_kql(query):
    try:
        response = client.execute(database, query)
        return dataframe_from_result_table( response.primary_results[0])
    except Exception as e:
        print(f"An error occurred: {e}")
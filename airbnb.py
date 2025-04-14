import os
import random
import string
import gcsfs
import polars as pl
from google.cloud import bigquery, storage
from google.cloud.exceptions import NotFound

def import_raw_file(dataset, city, year, month, day):
    bucket_name = os.environ["GOOGLE_BUCKET_NAME"]
    url = f"https://data.insideairbnb.com/{city}/{format_date(year, month, day)}/data/{dataset}.csv.gz"
    df = pl.read_csv(url).with_columns(snapshot_date=pl.lit(format_date(year, month, day)))
    fs = gcsfs.GCSFileSystem()
    object_uri = gcs_object_uri(bucket_name, dataset, city, year, month, day)
    with fs.open(object_uri, mode="wb") as f:
        df.write_parquet(f)

def import_staging(dataset, city, year, month, day):
    bucket_name = os.environ["GOOGLE_BUCKET_NAME"]
    project = os.environ["GOOGLE_PROJECT"]
    client = bigquery.Client()
    bigquery_dataset = "airbnb"
    client.create_dataset(client.dataset(bigquery_dataset), exists_ok=True)
    name = f"{dataset}-{city.replace('/', '-')}-{format_date(year, month, day)}"
    external_table_name = f"{project}.{bigquery_dataset}.{name}_{''.join(random.choices(string.ascii_lowercase, k=10))}"
    object_uri = gcs_object_uri(bucket_name, dataset, city, year, month, day)
    create_external_table_from_parquet(client, external_table_name, object_uri)
    table_name = f"{project}.{bigquery_dataset}.staging_{dataset}"
    create_table(client, table_name, external_table_name)
    merge_table(client, external_table_name, table_name, ["id", "snapshot_date"])
    client.delete_table(external_table_name)

def format_date(year, month, day):
    return f"{year:04d}-{month:02d}-{day:02d}"

def gcs_object_uri(bucket_name, dataset, city, year, month, day):
    return f"gs://{bucket_name}/{dataset}-{city.replace('/', '-')}-{format_date(year, month, day)}.parquet"

def create_external_table_from_parquet(client, table_name, source_uri):
    external_config = bigquery.ExternalConfig("PARQUET")
    external_config.source_uris = [source_uri]
    table = bigquery.Table(table_name)
    table.external_data_configuration = external_config
    client.create_table(table, exists_ok=True)

def create_table(client, table_name, source_schema_table_name):
    table = bigquery.Table(table_name)
    table.schema = client.get_table(source_schema_table_name).schema
    table = client.create_table(table, exists_ok=True)

def merge_table(client, source, target, key_columns):
    source_table = client.get_table(source)
    target_table = client.get_table(target)

    source_columns = {field.name for field in source_table.schema}
    target_columns = {field.name for field in target_table.schema}

    common_columns = source_columns.intersection(target_columns)

    join_condition = " AND ".join([f"t.{k} = s.{k}" for k in key_columns])

    source_select = ", ".join([f"{col} AS {col}" for col in common_columns])

    insert_columns = ", ".join([col for col in common_columns])
    insert_values = ", ".join([f"s.{col}" for col in common_columns])

    query = f"""
        MERGE INTO `{target}` AS t
        USING (SELECT {source_select} FROM `{source}`) AS s
        ON {join_condition}
        WHEN NOT MATCHED THEN
          INSERT ({insert_columns})
          VALUES ({insert_values})
    """

    query_job = client.query(query)
    return query_job.result()

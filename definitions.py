from datetime import datetime
import json
import dagster as dg
from dagster_dbt import dbt_assets, DbtCliResource, DbtProject
from pathlib import Path
import airbnb

partitions = dg.StaticPartitionsDefinition(["2024-03-22", "2024-06-15", "2024-09-11", "2024-12-12", "2025-03-05"])
partition_key_format = "%Y-%m-%d"
dbt_project_directory = Path(__file__).absolute().parent / "dbt"
dbt_project = DbtProject(project_dir=dbt_project_directory)
dbt_resource = DbtCliResource(project_dir=dbt_project)
dbt_project.prepare_if_dev()


@dg.asset(partitions_def=partitions)
def raw_listings(context):
    date = datetime.strptime(context.partition_key, partition_key_format)
    airbnb.import_raw_file("listings", "italy/lazio/rome", date.year, date.month, date.day)


@dg.asset(partitions_def=partitions, deps=[raw_listings])
def staging_listings(context):
    date = datetime.strptime(context.partition_key, partition_key_format)
    airbnb.import_staging("listings", "italy/lazio/rome", date.year, date.month, date.day)


@dg.asset(partitions_def=partitions)
def raw_reviews(context):
    date = datetime.strptime(context.partition_key, partition_key_format)
    airbnb.import_raw_file("reviews", "italy/lazio/rome", date.year, date.month, date.day)


@dg.asset(partitions_def=partitions, deps=[raw_reviews])
def staging_reviews(context):
    date = datetime.strptime(context.partition_key, partition_key_format)
    airbnb.import_staging("reviews", "italy/lazio/rome", date.year, date.month, date.day)


@dbt_assets(partitions_def=partitions, manifest=dbt_project.manifest_path)
def dbt_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    dbt_vars = {"snapshot_date": context.partition_key}
    dbt_args = ["build", "--vars", json.dumps(dbt_vars)]
    yield from dbt.cli(dbt_args, context=context).stream()


defs = dg.Definitions(
    assets=[raw_listings, staging_listings, raw_reviews, staging_reviews, dbt_models],
    resources={"dbt": dbt_resource},
    executor=dg.in_process_executor,
)

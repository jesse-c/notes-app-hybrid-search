import json

import pyarrow.parquet as pq
import structlog
import tomllib
from tqdm import tqdm

log = structlog.get_logger()

# Load configuration
log.debug("config", status="loading")
with open("config.toml", "rb") as f:
    config = tomllib.load(f)
log.debug("config", status="loaded")

# Load Parquet file
parquet_file = config["data"]["input_file"]
table = pq.read_table(parquet_file)

# Transform to row-based JSONL
output_file = config["data"]["output_file"]

with open(output_file, "w") as f:
    for row in tqdm(table.to_pylist()):
        put = {"put": f"id:entries:entries::{row["id"]}", "fields": row}
        json.dump(put, f)
        f.write("\n")

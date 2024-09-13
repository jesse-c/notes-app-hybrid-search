import csv
import json
from pathlib import Path

import structlog
import tomllib
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

log = structlog.get_logger()

# Load configuration
log.debug("config", status="loading")
with open("config.toml", "rb") as f:
    config = tomllib.load(f)
log.debug("config", status="loaded")

log.debug("model", status="loading")
model = SentenceTransformer(config["model"]["name"])
log.debug("model", status="loaded")


input_file = Path(config["data"]["input_file"])
output_file = Path(config["data"]["output_file"])

with input_file.open("r") as infile:
    reader = csv.reader(infile)
    actual_headers = next(reader)

    # Find column indices
    id_index = actual_headers.index("id")
    title_index = actual_headers.index("title")
    body_index = actual_headers.index("body")

    # Prepare data for Parquet
    with open(output_file, "w") as f:
        for row in tqdm(reader):
            fields = {
                "id": row[id_index],
                "title": row[title_index],
                "body": row[body_index],
            }
            put = {
                "put": f"id:entries:entries::{row[id_index]}",
                "fields": fields,
            }
            json.dump(put, f)
            f.write("\n")

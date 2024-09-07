import csv
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
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

log.debug("embeddings", status="generating")
with input_file.open("r") as infile:
    reader = csv.reader(infile)
    actual_headers = next(reader)

    # Find column indices
    id_index = actual_headers.index("id")
    title_index = actual_headers.index("title")
    body_index = actual_headers.index("body")

    # Prepare data for Parquet
    ids = []
    titles = []
    bodies = []
    body_embeddings = []

    for row in tqdm(reader):
        ids.append(row[id_index])
        titles.append(row[title_index])
        bodies.append(row[body_index])
        body_embedding = model.encode(row[body_index])
        body_embeddings.append(body_embedding)
log.debug("embeddings", status="generated")

# Create PyArrow Table
log.debug("table", status="generating")
table = pa.Table.from_arrays(
    [
        pa.array(ids),
        pa.array(titles),
        pa.array(bodies),
        pa.array(body_embeddings),
    ],
    names=["id", "title", "body", "body_embedding"],
)
log.debug("table", status="generated")

# Write to Parquet file
log.debug("table", status="writing")
pq.write_table(table, output_file)
log.debug("table", status="wrote")

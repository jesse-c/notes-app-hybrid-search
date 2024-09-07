import numpy as np
import tomllib
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

import structlog

log = structlog.get_logger()

# Load configuration
log.debug("config", status="loading")
with open("config.toml", "rb") as f:
    config = tomllib.load(f)
log.debug("config", status="loaded")

# Read sentences from input file
log.debug("sentences", status="loading")
with open(config["data"]["input_file"], "r") as f:
    sentences = f.readlines()
log.debug("sentences", status="loaded")

# Remove any leading/trailing whitespace
log.debug("sentences", status="stripping")
sentences = [s.strip() for s in sentences]
log.debug("sentences", status="stripped")

log.debug("model", status="loading")
model = SentenceTransformer(config["model"]["name"])
log.debug("model", status="loaded")

log.debug("embeddings", status="generating")
embeddings = []

for i in tqdm(range(0, len(sentences), config["embedding"]["batch_size"])):
    batch = sentences[i : i + config["embedding"]["batch_size"]]
    batch_embeddings = model.encode(batch)
    embeddings.extend(np.array(batch_embeddings))

log.debug("embeddings", status="generated")


# Save embeddings to a file without scientific notation
log.debug("embeddings", status="saving")
np.savetxt(
    config["data"]["output_file"],
    embeddings,
    delimiter=config["embedding"]["delimiter"],
    fmt=config["embedding"]["float_format"],
)
log.debug("embeddings", status="save")

import tomllib
import csv
from pathlib import Path

from tqdm import tqdm
import structlog

log = structlog.get_logger()

# Load configuration
with open("config.toml", "rb") as f:
    config = tomllib.load(f)

# Read headers from headers_file
with open(config["data"]["headers_file"], "r") as f:
    expected_headers = f.read().strip().split("\n")

# Read headers from input_file
input_file = Path(config["data"]["input_file"])
output_file = Path(config["data"]["output_file"])

with input_file.open("r") as infile:
    total_notes = sum(1 for line in infile) - 1


with input_file.open("r") as infile, output_file.open("w") as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    actual_headers = next(reader)

    # Compare headers
    if set(expected_headers) == set(actual_headers):
        log.info("headers match")
    else:
        log.error(
            "headers mismatch",
            missing=set(expected_headers) - set(actual_headers),
            extra=set(actual_headers) - set(expected_headers),
        )

    # Find column indices
    note_id_index = actual_headers.index("Note ID")
    title_index = actual_headers.index("Title")
    plaintext_index = actual_headers.index("Note Plaintext")

    # Write header to output file
    writer.writerow(["id", "title", "sentence"])

    log.info(f"total notes: {total_notes}")

    total_sentences = 1

    # Process each note
    for row in tqdm(reader, total=total_notes):
        try:
            id = row[note_id_index]
            title = row[title_index]
            plaintext = row[plaintext_index]

            # Split plaintext into sentences and write to output
            for sentence in plaintext.split("\n"):
                if sentence.strip():  # Only write non-empty sentences
                    total_sentences = total_sentences + 1
                    writer.writerow([id, title, sentence.strip()])
        except IndexError:
            log.error("Unexpected row format", row=row)
            continue

    log.info(f"total sentences: {total_sentences}")

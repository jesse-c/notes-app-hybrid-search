import asyncio
import os
import shutil

import structlog
import tomllib
from huggingface_hub import hf_hub_download

log = structlog.get_logger()

# Load configuration
log.debug("config", status="loading")
with open("config.toml", "rb") as f:
    config = tomllib.load(f)
log.debug("config", status="loaded")

SOURCE_FILES = [
    "onnx/model.onnx",
    "tokenizer.json",
]


async def download_file(file_path):
    local_path = hf_hub_download(
        repo_id=config["model"]["name"],
        filename=file_path,
        local_dir=config["data"]["output_dir"],
    )

    move_to_top_dir(local_path)


def move_to_top_dir(file_path):
    output_dir = config["data"]["output_dir"]
    file_name = os.path.basename(file_path)
    new_path = os.path.join(output_dir, file_name)
    if file_path != new_path:
        shutil.move(file_path, new_path)
        log.debug(f"moved {file_path} to {new_path}")

        # Delete the old nested directory if it's empty
        old_dir = os.path.dirname(file_path)
        while old_dir != output_dir:
            try:
                os.rmdir(old_dir)
                log.debug(f"removed empty directory: {old_dir}")
            except OSError:
                # Directory not empty or unable to delete, stop trying
                break
            old_dir = os.path.dirname(old_dir)


async def main():
    tasks = [download_file(file) for file in SOURCE_FILES]

    await asyncio.gather(*tasks)


asyncio.run(main())

"""Link things together.

> The clevis is a U-shaped piece that has holes at the end of the
  prongs to accept the clevis pin.

       _____
      /     \
     /       \
   ,'         `.
   |           |
   |           |
   |           |
===[]====o====[]===
   |___________|
      `---'
"""

import json
import os
from difflib import unified_diff

import tomllib


def _get_linked_value(link: list[dict]) -> str:
    completed_operations = [_operate(step) for step in link]

    return "".join(completed_operations)


def _operate(link: dict) -> str:
    match link["type"]:
        case "path":
            path = link["value"]
            if os.path.exists(path):
                return path

            raise ValueError(f"path {path} doesn't exist")
        case "toml":
            file_path = link["file"]
            key = link["key"]

            with open(file_path, "rb") as f:
                config = tomllib.load(f)

                # Traverse the config using the dot-separated key
                keys = key.split(".")

                value = config
                for k in keys:
                    value = value[k]

                return value

        case "span":
            file_path = link["file"]
            key = link["key"]

            # Parse the key to extract line number and character range
            line_raw, char_raw = key.split(":")
            line_idx = int(line_raw) - 1  # Convert to zero-based index
            char_start, char_end = map(int, char_raw.split("-"))

            with open(file_path, "r") as f:
                lines = f.readlines()

                # Ensure the line index is within bounds
                if line_idx < 0 or line_idx >= len(lines):
                    raise ValueError(f"line index {line_idx + 1} is out of bounds")

                line = lines[line_idx]

                # Ensure character ranges are within bounds
                if char_start < 1 or char_end > len(line):
                    raise ValueError(
                        f"character range {char_start}-{char_end} is out of bounds for line {line_idx + 1}"
                    )

                span = line[char_start - 1 : char_end]

                return span

        case _:
            raise ValueError(f"unknown type: {link['type']}")


def _get_state():
    with open("clevis.json", "r") as f:
        return json.load(f)


if __name__ == "__main__":
    state = _get_state()

    status: int = 0

    for key, value in state.items():
        print(f"checking {key}")

        expected_str = value["value"]

        a_str = _get_linked_value(value["a"]["link"])
        b_str = _get_linked_value(value["b"]["link"])

        diff_a = list(
            unified_diff(a_str, expected_str, fromfile="actual", tofile="expected")
        )

        if diff_a:
            print("differences found in A")
            print("".join(diff_a))
            status = 1
        else:
            print("no differences found in A")

        diff_b = list(
            unified_diff(b_str, expected_str, fromfile="actual", tofile="expected")
        )

        if diff_b:
            print("differences found in B")
            print("".join(diff_b))
            status = 1
        else:
            print("no differences found in B")

    exit(status)

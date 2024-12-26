# Hybrid search for Notes.app

One of the ways I use Notes.app is for having a Shortcut that creates a daily note, titled as the current day (e.g. "2024-09-08"), where I use it for journal-esque writings, dropping links to products or articles, project ideas, and anything.

Unfortunately, the keyword search in Notes.app isn't always sufficient. I'm sure Apple will add something like this eventually, and for now, I've cobbled something together.

## Usage

Run data targets, then top-level targets, and finally search targets.

For example:

- `ghq get git@github.com:threeplanetssoftware/apple_cloud_notes_parser.git`
- `just install` (`./`)
- `just step-00-to-step-01` (`./data`)
- `just headers-generate run` (`./data/01-from-notes-app-to-plaintext`)
- `step-01-to-step-02` (`./data`)
- `just headers-generate run` (`./data/02-plaintext-to-vespa-documents`)
- `just run` (`./data/03-huggingface-hub-to-local`)
- `just data-to-search model-to-search` (`./`)
- `just up health deploy feed-all query-cli-all` (`./search`)
- `just query-py-hybrid photography` (`./search`)

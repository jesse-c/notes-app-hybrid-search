data-to-search:
  cp data/03-embeddings-to-vespa-documents/output/vespa-all.jsonl search/vespa-all.jsonl

model-to-search:
  cp data/04-huggingface-hub-to-local/output/* search/app/models/

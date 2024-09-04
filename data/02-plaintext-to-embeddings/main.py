from sentence_transformers import SentenceTransformer
import numpy as np

sentences = [
    # "https://www.ruinedby.design\nRUINED BY DESIGN\nA design ethics and activism book by Mike Monteiro"
    "art"
]

model = SentenceTransformer("sentence-transformers/msmarco-MiniLM-L-6-v3")
embeddings = model.encode(sentences)

# Save embeddings to a file without scientific notation
np.savetxt("embeddings.txt", embeddings, delimiter=",", fmt="%.8f")

print("Embeddings have been saved to 'embeddings.txt'")

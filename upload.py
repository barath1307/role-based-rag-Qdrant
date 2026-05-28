from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import os

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create local Qdrant database
client = QdrantClient(":memory:")

collection_name = "company_docs"

# Create collection
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE
    )
)

documents_folder = "documents"

points = []

id_counter = 1

# Read all text files
for filename in os.listdir(documents_folder):

    if filename.endswith(".txt"):

        filepath = os.path.join(documents_folder, filename)

        with open(filepath, "r", encoding="utf-8", errors="ignore") as file:

            text = file.read()

        # Create embedding
        embedding = model.encode(text).tolist()

        # Extract role from filename
        role = filename.split("_")[0]

        # Create Qdrant point
        point = PointStruct(
            id=id_counter,
            vector=embedding,
            payload={
                "role": role,
                "text": text
            }
        )

        points.append(point)

        id_counter += 1

# Upload to Qdrant
client.upsert(
    collection_name=collection_name,
    points=points
)

print("Documents uploaded successfully!")

# Ask question
query = input("Ask a question: ")

role = input("Enter role: ")

query_embedding = model.encode(query).tolist()

# Search documents
results = client.query_points(
    collection_name=collection_name,
    query=query_embedding,
    limit=5
).points

print("\nResults:\n")

found = False

for result in results:

    if result.payload["role"] == role:

        print(result.payload["text"])
        found = True

if not found:
    print("No matching documents found for this role.")
import csv
import chromadb

# --- Load the Q/A pairs from the CSV ---
qa_pairs = []
with open("data/processed/qa_pairs.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        qa_pairs.append(row)

print(f"Loaded {len(qa_pairs)} Q/A pairs.")

# --- Set up Chroma with PERSISTENT storage (saved to disk) ---
client = chromadb.PersistentClient(path="chroma_db")

# Start fresh: delete the collection if it already exists, then recreate it.
# This makes the script safe to re-run without piling up duplicates.
try:
    client.delete_collection(name="ltw_qa")
except Exception:
    pass  # nothing to delete on the first run

collection = client.create_collection(name="ltw_qa")

# --- Add ALL questions to the collection ---
collection.add(
    documents=[pair["question"] for pair in qa_pairs],
    metadatas=[{"answer": pair["answer"], "source": pair["source"]} for pair in qa_pairs],
    ids=[f"pair_{i}" for i in range(len(qa_pairs))],
)

print(f"Embedded and stored {collection.count()} questions in Chroma.")
print("Database saved to: chroma_db/\n")

# --- Quick sanity-check query to confirm it works ---
query = "what time is the de-extinction session?"
print(f"TEST QUERY: {query}\n")

results = collection.query(query_texts=[query], n_results=3)

print("TOP 3 MATCHES BY MEANING:")
for i in range(len(results["documents"][0])):
    matched_question = results["documents"][0][i]
    matched_answer = results["metadatas"][0][i]["answer"]
    distance = results["distances"][0][i]
    print(f"  {i+1}. Q: {matched_question}")
    print(f"     A: {matched_answer}")
    print(f"     (distance: {distance:.3f})")
    print()
    
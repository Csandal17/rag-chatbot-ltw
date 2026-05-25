import os
import chromadb
from dotenv import load_dotenv
from anthropic import Anthropic

# --- Set up Claude (for the Tier 2 fallback) ---
load_dotenv()
anthropic_client = Anthropic()

# --- Open the EXISTING Chroma database (no re-embedding) ---
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection(name="ltw_qa")

print(f"Opened Chroma collection with {collection.count()} questions.\n")

# --- The threshold that decides "direct hit" vs "needs fallback" ---
DISTANCE_THRESHOLD = 0.5


def answer_with_claude(query, retrieved_pairs):
    """Tier 2: hand the retrieved context to Claude and ask it to synthesise an answer."""
    # Build a context block from the retrieved Q/A pairs
    context = ""
    for pair in retrieved_pairs:
        context += f"Q: {pair['question']}\nA: {pair['answer']}\n\n"

    prompt = f"""You are a helpful assistant for London Tech Week 2026.
Answer the user's question using ONLY the context below. 
If the context does not contain the answer, say you don't have that information.

Context:
{context}

User question: {query}

Answer:"""

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def retrieve(query):
    """Hybrid retrieval: Tier 1 direct hit, or Tier 2 Claude fallback."""
    # Get the top 3 matches (we need the closest for the decision, and the rest for fallback context)
    results = collection.query(query_texts=[query], n_results=3)

    closest_question = results["documents"][0][0]
    closest_answer = results["metadatas"][0][0]["answer"]
    distance = results["distances"][0][0]

    print(f"Query:           {query}")
    print(f"Closest match:   {closest_question}")
    print(f"Distance:        {distance:.3f}")

    if distance < DISTANCE_THRESHOLD:
        print(f"Decision:        DIRECT HIT (Tier 1)")
        print(f"Answer:          {closest_answer}")
        answer = closest_answer
        tier = 1                         # NEW: remember which tier answered
    else:
        print(f"Decision:        FALLBACK TO CLAUDE (Tier 2)")
        # Rebuild the top 3 as a list of dicts for context
        retrieved_pairs = []
        for i in range(len(results["documents"][0])):
            retrieved_pairs.append({
                "question": results["documents"][0][i],
                "answer": results["metadatas"][0][i]["answer"],
            })
        claude_answer = answer_with_claude(query, retrieved_pairs)
        print(f"Answer:          {claude_answer}")
        answer = claude_answer
        tier = 2                         # NEW: remember which tier answered

    print("-" * 60)
    # NEW: hand back a labelled tray (dictionary) with three things
    return {
        "answer": answer,
        "tier": tier,
        "distance": distance,
    }


# --- Test with a few different queries (only runs if you run this file directly) ---
if __name__ == "__main__":
    retrieve("what time is the de-extinction session?")        # Tier 1 direct hit
    retrieve("are there any sessions about failure or resilience?")  # Tier 2: phrased loosely, needs synthesis

    
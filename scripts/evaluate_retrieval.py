import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from backend.app.retrievers.chroma_retriever import ChromaRetriever
from backend.ingest.embedder import SecAIEmbedder

def evaluate():
    benchmark_path = project_root / "knowledge_base" / "benchmarks" / "retrieval_benchmark.json"
    
    if not benchmark_path.exists():
        print(f"❌ Benchmark file not found at {benchmark_path}")
        return

    with open(benchmark_path, "r") as f:
        benchmarks = json.load(f)

    print(f"🧪 Starting Retrieval Evaluation on {len(benchmarks)} questions...")
    
    # Initialize components
    retriever = ChromaRetriever()
    embedder = SecAIEmbedder(provider="local")
    
    hits = 0
    total = len(benchmarks)
    top_k = 5

    for item in benchmarks:
        question = item["question"]
        expected = item["expected_source"]
        
        # 1. Embed Query
        query_vector = embedder.embed_query(question)
        
        # 2. Retrieve
        results = retriever.search(query_vector, top_k=top_k)
        
        # 3. Check for "Hit"
        found = False
        for res in results:
            source = res["metadata"].get("source")
            if source == expected:
                found = True
                break
        
        if found:
            hits += 1
            print(f"✅ PASS: '{question}' found in {expected}")
        else:
            print(f"❌ FAIL: '{question}' - Expected {expected} not in top {top_k}")

    # 4. Final Report
    accuracy = (hits / total) * 100 if total > 0 else 0
    print("\n--- Evaluation Summary ---")
    print(f"Total Questions: {total}")
    print(f"Hits @ {top_k}: {hits}")
    print(f"Retrieval Accuracy (Recall): {accuracy:.2f}%")
    
    if accuracy < 80:
        print("\n⚠️  Recommendation: Consider adjusting chunk_size or using Hybrid Search.")

if __name__ == "__main__":
    evaluate()

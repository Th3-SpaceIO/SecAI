import sys
from pathlib import Path

# Add the project root to sys.path so we can import backend
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from backend.app.core.config import settings
from backend.ingest.document_loader import DocumentLoader
from backend.ingest.chunker import SecAIChunker
from backend.ingest.embedder import SecAIEmbedder
from backend.ingest.knowledge_graph.entity_extractor import SecurityEntityExtractor
from backend.app.retrievers.chroma_retriever import ChromaRetriever

def main():
    print("🚀 SecAI Ingestion Script Started")
    
    # 1. Loading
    print(f"📂 Scanning directory: {settings.RAW_DOCS_PATH}")
    loader = DocumentLoader()
    documents = loader.load_directory(settings.RAW_DOCS_PATH)
    
    if not documents:
        print("⚠️ No supported documents found.")
        return

    print(f"✅ Loaded {len(documents)} documents.")
    
    # 2. Chunking
    print("✂️  Chunking documents...")
    chunker = SecAIChunker(chunk_size=500, chunk_overlap=50)
    all_chunks = chunker.chunk_batch(documents)
    print(f"✅ Created {len(all_chunks)} chunks.")

    # 3. Knowledge Graph Extraction (Sample)
    # ... (skipping for brevity in logs)

    # 4. Embedding & Storage
    print("🧬 Initializing Embedder & Vector DB...")
    try:
        embedder = SecAIEmbedder(provider="local")
        retriever = ChromaRetriever()
        
        print(f"💾 Saving {len(all_chunks)} chunks to ChromaDB...")
        
        # Process in batches of 100 for efficiency
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            texts = [c["content"] for c in batch]
            embeddings = embedder.embed_texts(texts)
            retriever.add_chunks(batch, embeddings)
            print(f"   Processed {i + len(batch)} / {len(all_chunks)}")
        
        print("✅ Successfully synchronized Knowledge Base with Vector DB.")
        
    except Exception as e:
        print(f"❌ Storage failed: {str(e)}")

    print("\n--- Ingestion Summary ---")
    print(f"Files: {len(documents)}")
    print(f"Total Chunks: {len(all_chunks)}")
    print("\nNext Step:")
    print("Run 'python scripts/evaluate_retrieval.py' to test retrieval quality.")

if __name__ == "__main__":
    main()

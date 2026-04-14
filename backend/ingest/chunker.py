from typing import List, Dict


class DocumentChunker:
    def __init__(self, max_tokens: int = 500, overlap: int = 50):
        self.max_tokens = max_tokens
        self.overlap = overlap

    def chunk(self, document: Dict) -> List[Dict]:
        text = document["content"]
        metadata = document["metadata"]

        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self._estimate_tokens(para)

            # if adding paragraph exceeds limit → flush
            if current_tokens + para_tokens > self.max_tokens:
                if current_chunk:
                    chunks.append(self._build_chunk(current_chunk, metadata))
                    current_chunk, current_tokens = self._apply_overlap(current_chunk)

            current_chunk.append(para)
            current_tokens += para_tokens

        # flush remaining
        if current_chunk:
            chunks.append(self._build_chunk(current_chunk, metadata))

        return chunks

    def _build_chunk(self, paragraphs: List[str], metadata: Dict) -> Dict:
        text = "\n".join(paragraphs)

        return {
            "text": text,
            "metadata": {
                **metadata,
                "chunk_size": self._estimate_tokens(text)
            }
        }

    def _apply_overlap(self, chunk: List[str]):
        if not chunk:
            return [], 0

        # keep last N paragraphs as overlap context
        overlap_chunk = chunk[-2:] if len(chunk) >= 2 else chunk[-1:]

        overlap_text = "\n".join(overlap_chunk)
        return overlap_chunk, self._estimate_tokens(overlap_text)

    def _estimate_tokens(self, text: str) -> int:
        # simple approximation: 1 token ≈ 4 characters
        return max(1, len(text) // 4)
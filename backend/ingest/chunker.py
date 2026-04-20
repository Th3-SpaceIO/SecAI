from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class DocumentChunker:
    def __init__(self, max_tokens: int = 500, overlap: int = 50):
        if max_tokens <= 0:
            raise ValueError(f"max_tokens must be positive, got {max_tokens}")
        if overlap < 0 or overlap >= max_tokens:
            raise ValueError(f"overlap must be in [0, max_tokens), got {overlap}")

        self.max_tokens = max_tokens
        self.overlap = overlap

    def chunk(self, document: Dict) -> List[Dict]:
        """
        Split a document into overlapping token-bounded chunks.

        Args:
            document: dict with 'content' (str) and 'metadata' (dict)

        Returns:
            List of dicts, each with 'text' and 'metadata' (includes 'chunk_index',
            'chunk_size', and all original metadata keys).
        """
        if "content" not in document or "metadata" not in document:
            raise ValueError("document must have 'content' and 'metadata' keys")

        text: str = document["content"]
        metadata: Dict = document["metadata"]

        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

        chunks: List[Dict] = []
        current_chunk: List[str] = []
        current_tokens: int = 0

        for para in paragraphs:
            para_tokens = self._estimate_tokens(para)

            # BUG FIX: warn and sub-chunk paragraphs that exceed the hard limit
            if para_tokens > self.max_tokens:
                logger.warning(
                    "Paragraph exceeds max_tokens (%d > %d); splitting it.",
                    para_tokens, self.max_tokens,
                )
                # Flush whatever we have first
                if current_chunk:
                    chunks.append(self._build_chunk(current_chunk, metadata, len(chunks)))
                    current_chunk, current_tokens = self._apply_overlap(current_chunk)

                # Split the oversized paragraph into sub-chunks
                for sub in self._split_large_paragraph(para):
                    chunks.append(self._build_chunk([sub], metadata, len(chunks)))
                continue

            # Normal case: flush when adding this paragraph would overflow
            if current_tokens + para_tokens > self.max_tokens:
                if current_chunk:
                    chunks.append(self._build_chunk(current_chunk, metadata, len(chunks)))
                    # BUG FIX: overlap now respects self.overlap token budget
                    current_chunk, current_tokens = self._apply_overlap(current_chunk)

            current_chunk.append(para)
            current_tokens += para_tokens

        # Flush any remaining content
        if current_chunk:
            chunks.append(self._build_chunk(current_chunk, metadata, len(chunks)))

        return chunks

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_chunk(self, paragraphs: List[str], metadata: Dict, index: int) -> Dict:
        text = "\n".join(paragraphs)
        return {
            "text": text,
            "metadata": {
                **metadata,
                "chunk_index": index,                         # added: useful for ordering
                "chunk_size": self._estimate_tokens(text),
            },
        }

    def _apply_overlap(self, chunk: List[str]):
        """
        Return the tail of `chunk` whose total tokens fit within self.overlap,
        along with its token count.

        BUG FIX: previously always kept the last 2 paragraphs regardless of
        self.overlap; now we walk backward and respect the token budget.
        """
        if not chunk:
            return [], 0

        overlap_paragraphs: List[str] = []
        tokens_so_far = 0

        for para in reversed(chunk):
            para_tokens = self._estimate_tokens(para)
            if tokens_so_far + para_tokens > self.overlap:
                break
            overlap_paragraphs.insert(0, para)
            tokens_so_far += para_tokens

        return overlap_paragraphs, tokens_so_far

    def _split_large_paragraph(self, para: str) -> List[str]:
        """
        Naively split an oversized paragraph into max_tokens-sized pieces
        by splitting on sentence boundaries first, then hard-cutting.
        """
        import re
        # Try to split on sentence endings first
        sentences = re.split(r'(?<=[.!?])\s+', para)

        sub_chunks: List[str] = []
        current_words: List[str] = []
        current_tokens = 0

        for sentence in sentences:
            s_tokens = self._estimate_tokens(sentence)
            if current_tokens + s_tokens > self.max_tokens and current_words:
                sub_chunks.append(" ".join(current_words))
                current_words, current_tokens = [], 0
            current_words.append(sentence)
            current_tokens += s_tokens

        if current_words:
            sub_chunks.append(" ".join(current_words))

        return sub_chunks or [para]

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Approximate token count: 1 token ≈ 4 characters."""
        return max(1, len(text) // 4)
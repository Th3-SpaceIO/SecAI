from typing import List
from abc import ABC, abstractmethod


from sentence_transformers import SentenceTransformer
import torch
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
import time
from logging import getLogger


logger = getLogger(__name__)

#==============================#
#    BASE EMBEDDER CLASS
#==============================#

class BaseEmbedder(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        pass




#==============================#
#  HUGGINGFACE EMBEDDER
#==============================#


class HuggingFaceEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.device = (
            "cuda" if torch.cuda.is_available()
            else "mps" if torch.backends.mps.is_available()
            else "cpu"
        )
        self.batch_size = 32 if self.device == "cpu" else 128
        self.model = SentenceTransformer(model_name, device=self.device)

    def embed(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            batch_size=self.batch_size,
            normalize_embeddings=True,
        )
        return embeddings.tolist()
    



#================================#
#      OPEN AI EMBEDDER          #
#================================#


_OPENAI_BATCH_LIMIT = 512 

class OpenAIEmbedder(BaseEmbedder):
    def __init__(self, api_key: str, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name
        self._client = OpenAI(api_key=api_key)

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        # FIX: batch to stay within API limits
        all_embeddings: List[List[float]] = []
        for i in range(0, len(texts), _OPENAI_BATCH_LIMIT):
            batch = texts[i : i + _OPENAI_BATCH_LIMIT]
            all_embeddings.extend(self._embed_batch(batch))

        return all_embeddings

    def _embed_batch(self, texts: List[str], retries: int = 3) -> List[List[float]]:
        for attempt in range(retries):
            try:
                response = self._client.embeddings.create(
                    input=texts,
                    model=self.model_name,
                )
                return [
                    e.embedding
                    for e in sorted(response.data, key=lambda x: x.index)
                ]

            except RateLimitError:
                wait = 2 ** attempt  # exponential backoff: 1s, 2s, 4s
                logger.warning("Rate limited by OpenAI, retrying in %ds...", wait)
                time.sleep(wait)

            except APIConnectionError as e:
                raise ConnectionError(f"Could not reach OpenAI API: {e}") from e

            except APIError as e:
                raise RuntimeError(f"OpenAI API error: {e}") from e

        raise RuntimeError(f"OpenAI embedding failed after {retries} retries")





if __name__ == "__main__":
    # Example usage
    start_time = time.time()
    embedder = HuggingFaceEmbedder()
    texts = ["welcome to nhs"]
    embeddings = embedder.embed(texts)
    end_time = time.time()

    print(embeddings)
    print(f"Generated {len(embeddings)} embeddings in {end_time - start_time:.2f} seconds.")
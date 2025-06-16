from __future__ import annotations

from pathlib import Path
from typing import List

from llama_index import Document, ServiceContext, StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore


class CodeVectorIndex:
    """Manage FAISS-based vector index of code snippets."""

    def __init__(self, persist_dir: str = "index_data", model_name: str = "Salesforce/codet5p-110m") -> None:
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.embed_model = HuggingFaceEmbedding(model_name=model_name)

        index_file = self.persist_dir / "faiss.index"
        if index_file.exists():
            self.vector_store = FaissVectorStore.from_persist_dir(persist_dir)
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            self.index = VectorStoreIndex.load_from_persist_dir(
                persist_dir, service_context=ServiceContext.from_defaults(embed_model=self.embed_model), storage_context=storage_context
            )
        else:
            self.vector_store = FaissVectorStore(dim=self.embed_model.embedding_size)
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            self.index = VectorStoreIndex(
                [], service_context=ServiceContext.from_defaults(embed_model=self.embed_model), storage_context=storage_context
            )
            self.index.storage_context.persist(persist_dir)

    def add_code(self, filename: str, content: str) -> None:
        doc = Document(text=content, metadata={"file": filename})
        self.index.insert(doc)
        self.index.storage_context.persist(self.persist_dir)

    def query(self, text: str, top_k: int = 3) -> List[str]:
        query_engine = self.index.as_query_engine(similarity_top_k=top_k)
        response = query_engine.query(text)
        return [node.metadata.get("file", "") for node in response.source_nodes]

import os
import json
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import datetime
from typing import List, Dict, Any, Optional
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class VectorMemory:
    """
    Hệ thống lưu trữ vector cho tri thức dài hạn (Persistent LTM).
    Uses ChromaDB (Local Vector DB) and SentenceTransformers (Local Embeddings).
    """
    def __init__(self, db_path: str = os.path.join(config.WORKSPACE_ROOT, "data", "vector_db")):
        self.db_path = db_path
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize ChromaDB Client
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Initialize Embedding Model (Local)
        # using all-MiniLM-L6-v2 for speed and efficiency
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or Create Collection
        self.collection = self.client.get_or_create_collection(name="agent_memory")

    async def add_text(self, text: str, metadata: Dict[str, Any] = None):
        """Alias for add_memory for compatibility."""
        await self.add_memory(text, metadata=metadata)

    async def add_memory(self, text: str, category: str = "general", metadata: Dict[str, Any] = None):
        """Tạo embedding và lưu tri thức vào phân vùng cụ thể."""
        try:
            # Generate ID based on timestamp
            doc_id = f"{category}_{datetime.datetime.now().timestamp()}"
            
            # Embed using local model
            embedding = self.embedding_model.encode(text).tolist()
            
            meta = metadata or {}
            meta["category"] = category
            meta["timestamp"] = datetime.datetime.now().isoformat()
            
            self.collection.add(
                documents=[text],
                embeddings=[embedding],
                metadatas=[meta],
                ids=[doc_id]
            )
        except Exception as e:
            print(f"Vector Error (add): {e}")

    async def recall(self, query: str, top_k: int = 3, category: str = None) -> str:
        """Truy xuất tri thức liên quan dưới dạng text để đưa vào context."""
        results = await self.search(query, top_k, category=category)
        if not results:
            return ""
        
        return "\n".join([f"- RECALLED: {res['text']}" for res in results])

    async def search(self, query: str, top_k: int = 3, category: str = None) -> List[Dict[str, Any]]:
        """Tìm kiếm nội dung liên quan nhất."""
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            
            where_filter = {"category": category} if category else None
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter
            )
            
            # Format results
            formatted_results = []
            if results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "id": results['ids'][0][i]
                    })
            
            return formatted_results
        except Exception as e:
            print(f"Vector Error (search): {e}")
            return []

if __name__ == "__main__":
    # Test
    import asyncio
    async def test():
        vm = VectorMemory()
        await vm.add_text("FastAPI là một framework Python hiện đại.", {"source": "manual"})
        res = await vm.search("framework web python")
        print(f"Kết quả tìm kiếm: {res[0]['text'] if res else 'Không tìm thấy'}")
    
    # asyncio.run(test())

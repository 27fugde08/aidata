import os
import json
import google.generativeai as genai
import numpy as np
import datetime
from typing import List, Dict, Any, Optional
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class VectorMemory:
    """
    Hệ thống lưu trữ vector cho tri thức dài hạn (Persistent LTM).
    Sử dụng Gemini Embeddings và phân vùng tri thức.
    """
    def __init__(self, db_path: str = config.VECTOR_DB_PATH):
        self.db_path = db_path
        self.data = self._load_db()
        genai.configure(api_key=config.GEMINI_API_KEY)

    def _load_db(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_db(self):
        """Lưu DB an toàn (nguyên tử)."""
        temp_path = f"{self.db_path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        os.replace(temp_path, self.db_path)

    async def add_text(self, text: str, metadata: Dict[str, Any] = None):
        """Alias for add_memory for compatibility."""
        await self.add_memory(text, metadata=metadata)

    async def add_memory(self, text: str, category: str = "general", metadata: Dict[str, Any] = None):
        """Tạo embedding và lưu tri thức vào phân vùng cụ thể."""
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            embedding = result['embedding']
            
            self.data.append({
                "text": text,
                "vector": embedding,
                "category": category,
                "timestamp": datetime.datetime.now().isoformat(),
                "metadata": metadata or {}
            })
            self._save_db()
        except Exception as e:
            print(f"Vector Error (add): {e}")

    async def recall(self, query: str, top_k: int = 3, category: str = None) -> str:
        """Truy xuất tri thức liên quan dưới dạng text để đưa vào context."""
        results = await self.search(query, top_k)
        if not results:
            return ""
        
        # Lọc theo category nếu cần
        filtered = [res for res in results if not category or res.get("category") == category]
        return "\n".join([f"- RECALLED: {res['text']}" for res in filtered])

    async def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Tìm kiếm nội dung liên quan nhất bằng Cosine Similarity."""
        if not self.data:
            return []

        try:
            query_result = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type="retrieval_query"
            )
            query_vec = np.array(query_result['embedding'])

            results = []
            for item in self.data:
                item_vec = np.array(item['vector'])
                # Cosine Similarity
                similarity = np.dot(query_vec, item_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(item_vec))
                results.append((similarity, item))

            # Sắp xếp theo độ tương đồng giảm dần
            results.sort(key=lambda x: x[0], reverse=True)
            return [res[1] for res in results[:top_k]]
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

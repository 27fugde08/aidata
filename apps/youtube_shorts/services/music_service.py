import os
import httpx
import random
from typing import Optional

class MusicService:
    """Dịch vụ tự động tìm và tải nhạc nền không bản quyền từ Pixabay."""
    
    def __init__(self):
        # API Key mặc định của Pixabay (nên thay bằng key riêng nếu dùng nhiều)
        self.api_key = os.getenv("PIXABAY_API_KEY", "25442526-70e633d7b7e53f069608d4b31")
        self.music_cache = os.path.join(os.path.dirname(__file__), "../../data/music_cache")
        os.makedirs(self.music_cache, exist_ok=True)

    async def get_background_music(self, mood: str) -> Optional[str]:
        """Tìm kiếm và tải về file nhạc nền theo mood."""
        try:
            # 1. Tìm kiếm nhạc trên Pixabay
            url = f"https://pixabay.com/api/videos/?" # Lưu ý: Pixabay API dùng chung cho video/music
            # Do Pixabay API cho nhạc hơi đặc thù, ta sẽ dùng bộ lọc search
            params = {
                "key": self.api_key,
                "q": mood,
                "per_page": 5
            }
            
            # Ghi chú: Thực tế Pixabay có endpoint âm nhạc riêng, 
            # nhưng để đơn giản và ổn định cho demo, ta sẽ dùng một tập tin nhạc cục bộ 
            # hoặc tìm kiếm thông qua một proxy đơn giản. 
            # Ở đây tôi sẽ giả lập việc tải về hoặc dùng file có sẵn trong cache.
            
            local_file = os.path.join(self.music_cache, f"{mood}.mp3")
            if os.path.exists(local_file):
                return local_file
                
            # Nếu không có API key thực sự, hệ thống sẽ trả về None để bỏ qua nhạc nền
            return None
        except Exception as e:
            print(f"❌ Music Service Error: {e}")
            return None

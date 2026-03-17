import os
import asyncio
from typing import Dict, Any, Optional
from spaceofduy.projects.douyin_automation.backend.core.scraper import DouyinScraper

class DouyinService:
    """
    Service quản lý các hoạt động liên quan đến video Douyin.
    """
    def __init__(self):
        # Đường dẫn lưu trữ cho Douyin
        self.output_dir = os.path.join(os.getcwd(), "outputs", "douyin")
        os.makedirs(self.output_dir, exist_ok=True)
        self.scraper = DouyinScraper(self.output_dir)

    async def get_video_details(self, url: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin chi tiết video Douyin."""
        # Clean URL if it's a share link with extra text
        clean_url = self._extract_url(url)
        return await self.scraper.get_video_info(clean_url)

    async def download_real_video(self, url: str, video_id: str, filename: str = None) -> Optional[str]:
        """Tải video Douyin thực tế (không logo)."""
        clean_url = self._extract_url(url)
        if not filename:
            filename = f"douyin_{video_id}"
        
        return await self.scraper.download_video(clean_url, filename)

    def _extract_url(self, text: str) -> str:
        """Trích xuất URL từ chuỗi văn bản (đề phòng người dùng dán cả đoạn share)."""
        url_pattern = re.compile(r'https?://[^\s]+')
        match = url_pattern.search(text)
        return match.group(0) if match else text

import re # Thêm import re ở đây cho sạch

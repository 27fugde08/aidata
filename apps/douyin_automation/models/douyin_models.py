from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict

class DouyinVideoRequest(BaseModel):
    url: str

class DouyinVideoResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = ""
    author: str
    author_id: Optional[str] = ""
    thumbnail: Optional[str] = ""
    original_url: str
    video_url: str
    duration: int
    like_count: Optional[int] = 0
    comment_count: Optional[int] = 0
    tags: Optional[List[str]] = []

class DownloadRequest(BaseModel):
    url: str
    video_id: str
    filename: Optional[str] = None

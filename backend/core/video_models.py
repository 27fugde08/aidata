from sqlalchemy import create_all, create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "shorts.db")
engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    platform = Column(String)
    title = Column(String)
    duration = Column(Float)
    file_path = Column(String)
    thumbnail = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    clips = relationship("Clip", back_populates="video")

class Clip(Base):
    __tablename__ = "clips"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    start_time = Column(Float)
    end_time = Column(Float)
    output_path = Column(String)
    status = Column(String, default="pending") # pending, completed, failed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    video = relationship("Video", back_populates="clips")

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()

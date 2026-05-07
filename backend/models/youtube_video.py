from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class YouTubeVideo(Base):
    __tablename__ = "youtube_videos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, nullable=False)  # YouTube video ID (from URL)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    channel = Column(String, nullable=True)
    topic_slug = Column(String, nullable=False)  # links to Topic.slug
    category = Column(String, nullable=True)  # "tutorial", "demo", "defense", "ctf"
    duration = Column(Integer, nullable=True)  # seconds
    published_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # No direct back-populate needed; simple lookup table

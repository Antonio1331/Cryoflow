from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    region_name = Column(String, nullable=True)
    snow_covered_area_km2 = Column(Float)
    total_area_km2 = Column(Float)
    snow_cover_percentage = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
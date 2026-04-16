from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./prompt_optimizer.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class OptimizationRecord(Base):
    __tablename__ = "optimization_records"

    id = Column(Integer, primary_key=True, index=True)
    original_prompt = Column(Text, nullable=False)
    optimized_prompt = Column(Text, nullable=True)
    domain = Column(String(100), default="general")
    original_score = Column(Float, nullable=True)
    optimized_score = Column(Float, nullable=True)
    improvement = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    prompt = Column(Text, nullable=False)
    domain = Column(String(100), default="general")
    score = Column(Float, nullable=True)
    use_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    user_input = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    response_score = Column(Float, nullable=True)
    domain = Column(String(100), default="general")
    created_at = Column(DateTime, default=datetime.utcnow)


class CompareRecord(Base):
    __tablename__ = "compare_records"

    id = Column(Integer, primary_key=True, index=True)
    prompt_a = Column(Text, nullable=False)
    prompt_b = Column(Text, nullable=False)
    test_input = Column(Text, nullable=False)
    response_a = Column(Text, nullable=True)
    response_b = Column(Text, nullable=True)
    score_a = Column(Float, nullable=True)
    score_b = Column(Float, nullable=True)
    winner = Column(String(10), nullable=True)
    domain = Column(String(100), default="general")
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

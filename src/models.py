import os

from dotenv import load_dotenv
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    create_engine,
    func,
    text,
)
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv()

Base = declarative_base()


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    term = Column(String(20))
    major = Column(String(50))
    course_number = Column(String(10))
    short_title = Column(String(50))
    full_title = Column(String(100))
    description = Column(Text)
    has_details = Column(Boolean, default=False)
    is_registerable = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    hub_attributes = Column(JSON)
    units = Column(String(10))

    sections = relationship("Section", back_populates="course")


class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    class_section = Column(String(10))
    class_type = Column(String(10))
    professor_name = Column(String(100))
    class_capacity = Column(Integer)
    enrollment_total = Column(Integer)
    enrollment_available = Column(Integer)
    days = Column(String(50))
    start_time = Column(String(50))
    end_time = Column(String(50))
    location = Column(String(255))
    is_active = Column(Boolean, default=True)
    professor_overall_quality = Column(Float)
    professor_difficulty = Column(Float)
    professor_link = Column(String(255))
    last_rmp_update = Column(DateTime)

    course = relationship("Course", back_populates="sections")


database_url = URL.create(
    drivername="postgresql",
    username=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT"),
    database=os.getenv("PGDATABASE"),
)


def clear_database(db):
    db.query(Section).delete()
    db.query(Course).delete()
    db.commit()


engine = create_engine(database_url)

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from sqlalchemy import create_engine, Column, Integer, String, Time, ForeignKey, Boolean, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.engine import URL
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    term = Column(String(20))
    major = Column(String(50))
    course_number = Column(String(10))
    short_title = Column(String(50))
    full_title = Column(String(100))
    description = Column(Text)
    has_details = Column(Boolean, default=False)
    is_registerable = Column(Boolean, default=False)

    sections = relationship("Section", back_populates="course")

class Section(Base):
    __tablename__ = 'sections'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    class_section = Column(String(10))
    class_type = Column(String(10))
    professor_name = Column(String(100))
    class_capacity = Column(Integer)
    enrollment_total = Column(Integer)
    enrollment_available = Column(Integer)
    days = Column(String(50))
    start_time = Column(Time)
    end_time = Column(Time)
    location = Column(String(255))  
    is_active = Column(Boolean, default=True) 

    course = relationship("Course", back_populates="sections")
    
database_url = URL.create(
    drivername="postgresql",
    username=os.getenv("POSTGRES_USERNAME"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host="localhost",
    port=5432,
    database="scrape_bu"
)

engine = create_engine(database_url)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

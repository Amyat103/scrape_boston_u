from sqlalchemy import create_engine, Column, Integer, String, Time
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    term = Column(String(20))
    major = Column(String(50))
    course_number = Column(String(10))
    course_name = Column(String(100))
    class_type = Column(String(10))
    section_number = Column(String(10))
    professor_name = Column(String(100))
    class_capacity = Column(Integer)
    enrollment_total = Column(Integer)
    meeting_days = Column(String(50))
    start_time = Column(Time)
    end_time = Column(Time)
    building = Column(String(50))
    room = Column(String(50))
    description = Column(String(255))
    
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
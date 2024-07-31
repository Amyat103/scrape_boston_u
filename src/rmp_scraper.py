import json
import logging
import os
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Course, Section

load_dotenv()


def setup_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def get_rmp_data(professor_name):
    return {
        "overall_quality": 4.0,
        "difficulty": 3.5,
        "link": f'https://www.ratemyprofessors.com/search/teachers?query={professor_name.replace(" ", "%20")}',
    }


def update_professor_ratings():
    engine = create_engine(os.getenv("DB_URL"))
    Session = sessionmaker(bind=engine)
    session = Session()

    thirty_days_ago = datetime.now() - timedelta(days=30)
    professors_to_update = (
        session.query(Section.professor_name)
        .filter(
            (Section.last_rmp_update == None)
            | (Section.last_rmp_update < thirty_days_ago)
        )
        .distinct()
        .all()
    )

    for professor in professors_to_update:
        rmp_data = get_rmp_data(professor.professor_name)
        if rmp_data:
            session.query(Section).filter_by(
                professor_name=professor.professor_name
            ).update(
                {
                    "professor_overall_quality": rmp_data["overall_quality"],
                    "professor_difficulty": rmp_data["difficulty"],
                    "professor_link": rmp_data["link"],
                    "last_rmp_update": datetime.now(),
                }
            )
            logging.info(f"Updated RMP data for {professor.professor_name}")
        else:
            logging.info(f"No RMP data found for {professor.professor_name}")

    session.commit()
    session.close()


if __name__ == "__main__":
    setup_logging()
    update_professor_ratings()

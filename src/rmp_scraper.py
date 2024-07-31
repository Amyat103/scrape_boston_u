import logging
import os
import random
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Section

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)


def get_rmp_data(driver, professor_name):
    base_url = "https://www.ratemyprofessors.com/search/professors/124"
    search_url = f"{base_url}?q={professor_name.replace(' ', '%20')}"

    try:
        driver.get(search_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "TeacherCard__StyledTeacherCard-syjs0d-0")
            )
        )

        professor_cards = driver.find_elements(
            By.CLASS_NAME, "TeacherCard__StyledTeacherCard-syjs0d-0"
        )

        if not professor_cards:
            logger.warning(f"No professor cards found for {professor_name}")
            return None

        for card in professor_cards:
            name_element = card.find_element(
                By.CLASS_NAME, "CardName__StyledCardName-sc-1gyrgim-0"
            )
            card_name = name_element.text.replace("\n", " ").lower()
            if professor_name.lower() in card_name:
                quality_element = card.find_element(
                    By.CLASS_NAME, "CardNumRating__CardNumRatingNumber-sc-17t4b9u-2"
                )
                overall_quality = quality_element.text

                feedback_elements = card.find_elements(
                    By.CLASS_NAME, "CardFeedback__CardFeedbackNumber-lq6nix-2"
                )
                would_take_again = (
                    feedback_elements[0].text if len(feedback_elements) > 0 else "N/A"
                )
                difficulty = (
                    feedback_elements[1].text if len(feedback_elements) > 1 else "N/A"
                )

                link = card.get_attribute("href")

                return {
                    "overall_quality": float(overall_quality),
                    "would_take_again": would_take_again.replace("%", ""),
                    "difficulty": float(difficulty) if difficulty != "N/A" else None,
                    "link": link,
                }

        logger.warning(f"{professor_name} not found in search results")
        return None

    except TimeoutException:
        logger.error(f"Timeout while searching for {professor_name}")
    except NoSuchElementException as e:
        logger.error(f"Element not found for {professor_name}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error for {professor_name}: {e}")

    return None


def update_professor_ratings(force_update=False):
    print("Starting professor ratings update")
    engine = create_engine(os.getenv("DB_PUBLIC"))
    Session = sessionmaker(bind=engine)
    session = Session()

    driver = setup_driver()

    try:
        if force_update:
            professors_to_update = (
                session.query(Section.professor_name).distinct().all()
            )
        else:
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
        print(f"Found {len(professors_to_update)} professors to update")

        for professor in professors_to_update:
            if professor.professor_name:
                print(f"Processing {professor.professor_name}")
                rmp_data = get_rmp_data(driver, professor.professor_name)
                if rmp_data:
                    update_data = {
                        "professor_overall_quality": rmp_data["overall_quality"],
                        "professor_difficulty": rmp_data["difficulty"],
                        "professor_link": rmp_data["link"],
                        "last_rmp_update": datetime.now(),
                    }
                    session.query(Section).filter_by(
                        professor_name=professor.professor_name
                    ).update(update_data)
                    print(f"Updated data for {professor.professor_name}")
                else:
                    print(f"No data found for {professor.professor_name}")
            else:
                print("Encountered a section with no professor name")

            time.sleep(random.uniform(1, 3))

        session.commit()
        print("Finished updating professor ratings")

    except Exception as e:
        print(f"An error occurred while updating professor ratings: {str(e)}")
        session.rollback()

    finally:
        session.close()
        driver.quit()


if __name__ == "__main__":
    import sys

    force_update = "--force" in sys.argv
    update_professor_ratings(force_update)

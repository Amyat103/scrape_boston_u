import json
import logging
import multiprocessing
import os
import random
import time
from functools import partial

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import login
import user_profile
from models import Course, Section, SessionLocal, clear_database
from process import process_course, process_major
from scraper import Scraper

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="scraper.log",
    filemode="w",
)


def test_link(driver):
    test_link = os.getenv("TEST_LINK")

    driver.get(test_link)

    old_data = driver.find_element(By.TAG_NAME, "body").text
    data = json.loads(old_data)
    print(data)
    return data


# def process_major_chunk(major_chunk, db_url):
#     engine = create_engine(db_url)
#     SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#     db = SessionLocal()

#     try:
#         for major_code in major_chunk:
#             try:
#                 with db.begin():
#                     process_major(major_code, Scraper, db)
#             except Exception as e:
#                 logging.error(f"Error processing major {major_code}: {str(e)}")
#     finally:
#         db.close()


def process_major_chunk(major_chunk, db_url):
    logging.info(f"Starting to process chunk of {len(major_chunk)} majors")
    engine = None
    db = None
    driver = None

    total_courses = 0
    total_sections = 0

    try:
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        logging.info("Creating headless driver for chunk...")
        driver = user_profile.create_driver()
        logging.info("Creating browser for chunk...")
        browser = login.Browser(driver)
        logging.info("Creating scraper for chunk...")
        scraper = Scraper(browser)

        for major_code in major_chunk:
            try:
                logging.info(f"Starting to process major: {major_code}")
                courses = scraper.get_courses_from_major(major_code)["courses"]
                logging.info(f"Found {len(courses)} courses for {major_code}")

                for course_data in courses:
                    try:
                        course, sections = process_course(
                            course_data, db, major_code, scraper
                        )
                        total_courses += 1
                        total_sections += len(sections)
                        logging.info(
                            f"Processed course {course.course_number} with {len(sections)} sections"
                        )
                    except Exception as e:
                        logging.error(
                            f"Error processing course {course_data.get('catalog_nbr')}: {str(e)}"
                        )

                logging.info(f"Finished processing major: {major_code}")
            except Exception as e:
                logging.error(f"Error processing major {major_code}: {str(e)}")
                logging.exception("Exception details:")
    except Exception as e:
        logging.error(f"Error in process_major_chunk: {str(e)}")
        logging.exception("Exception details:")
    finally:
        logging.info("Closing database connection and quitting driver for chunk...")
        if db:
            db.close()
        if driver:
            driver.quit()
        if engine:
            engine.dispose()

        logging.info(
            f"Chunk summary: Processed {total_courses} courses and {total_sections} sections"
        )

    return total_courses, total_sections


def get_term_from_offerings(data):
    try:
        term = data["course_details"]["offerings"][0]["open_terms"][0]["strm"].strip()
        print(f"Extracted term: {term}")
        return term
    except (IndexError, KeyError) as e:
        print(f"Failed to extract term due to an error: {e}")
        print(f"Data received was: {json.dumps(data, indent=4)}")
        return None

    # def test_cascs():
    driver = None
    db = SessionLocal()

    try:
        driver = user_profile.create_driver()
        browser = login.Browser(driver)
        scraper = Scraper(browser)

        major = "CASCS"
        courses = scraper.get_courses_from_major(major)["courses"][:5]
        logging.info(f"Retrieved {len(courses)} courses for CASCS")

        for course_data in courses:
            try:
                process_course(course_data, db, major, scraper)
            except Exception as e:
                logging.error(
                    f"Error processing course {course_data.get('catalog_nbr')}: {str(e)}"
                )

    except Exception as e:
        logging.error(f"Error in test_cascs: {str(e)}")
    finally:
        if db:
            db.close()
        if driver:
            driver.quit()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_tests():
    driver = None
    db = SessionLocal()

    try:
        clear_database(db)
        driver = user_profile.create_driver()
        browser = login.Browser(driver)
        scraper = Scraper(browser)

        test_casaa(scraper, db)
        test_cascs(scraper, db)

    except Exception as e:
        logging.error(f"Error in run_tests: {str(e)}")
    finally:
        if db:
            db.close()
        if driver:
            driver.quit()


def test_casaa(scraper, db):
    major = "CASAA"
    courses = scraper.get_courses_from_major(major)["courses"][:5]
    logging.info(f"Retrieved {len(courses)} courses for CASAA")

    for course_data in courses:
        try:
            process_course(course_data, db, major, scraper)
        except Exception as e:
            logging.error(
                f"Error processing CASAA course {course_data.get('catalog_nbr')}: {str(e)}"
            )


def test_cascs(scraper, db):
    major = "CASCS"
    courses = scraper.get_courses_from_major(major)["courses"][:5]
    logging.info(f"Retrieved {len(courses)} courses for CASCS")

    for course_data in courses:
        try:
            process_course(course_data, db, major, scraper)
        except Exception as e:
            logging.error(
                f"Error processing CASCS course {course_data.get('catalog_nbr')}: {str(e)}"
            )


def main():
    db_url = os.getenv("DB_URL")
    driver = None

    try:
        logging.info("Creating initial driver...")
        driver = user_profile.create_driver()
        logging.info("Creating browser...")
        browser = login.Browser(driver)
        logging.info("Creating scraper...")
        scraper = Scraper(browser)

        logging.info("Attempting to retrieve majors...")
        majors = scraper.get_all_majors()

        if not majors or "subjects" not in majors:
            logging.error("Failed to retrieve majors or unexpected data structure")
            logging.debug(f"Majors data: {majors}")
            return

        logging.info(f"Retrieved {len(majors['subjects'])} majors")

        major_codes = [major["subject"] for major in majors["subjects"]]
        logging.info(f"First few major codes: {major_codes[:5]}")

        num_processes = 4
        logging.info(f"Setting up {num_processes} processes")

        chunk_size = len(major_codes) // num_processes
        major_chunks = [
            major_codes[i : i + chunk_size]
            for i in range(0, len(major_codes), chunk_size)
        ]

        if len(major_codes) % num_processes != 0:
            major_chunks[-1].extend(major_codes[num_processes * chunk_size :])

        logging.info(f"Split majors into {len(major_chunks)} chunks")

        logging.info("Starting multiprocessing pool...")
        with multiprocessing.Pool(processes=num_processes) as pool:
            process_chunk = partial(process_major_chunk, db_url=db_url)
            try:
                pool.map(process_chunk, major_chunks)
            except Exception as e:
                logging.error(f"Error in pool.map: {str(e)}")
                logging.exception("Exception details:")

        logging.info("Finished processing all majors")

    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        logging.exception("Exception details:")
    finally:
        logging.info("Closing initial driver...")
        if driver:
            driver.quit()


def main_subset():
    driver = None
    db = SessionLocal()

    try:
        driver = user_profile.create_driver()
        browser = login.Browser(driver)
        scraper = Scraper(browser)

        majors = scraper.get_all_majors()
        logging.info(f"Retrieved {len(majors['subjects'])} majors")

        test_majors = majors["subjects"][:4]
        logging.info(
            f"Testing with 4 majors: {[major['subject'] for major in test_majors]}"
        )

        for major in test_majors:
            major_code = major["subject"]
            try:
                process_major(major_code, scraper, db)
                logging.info(f"Finished processing major: {major_code}")
            except Exception as e:
                logging.error(f"Error processing major {major_code}: {str(e)}")

        logging.info("Finished processing test set of majors")

    except Exception as e:
        logging.error(f"Error in main_subset: {str(e)}")
    finally:
        if db:
            db.close()
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()
    # main_subset()

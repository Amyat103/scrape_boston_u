import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import login
import user_profile
import json
from scraper import Scraper
import time
from models import SessionLocal, Course, Section, clear_database
from process import process_course
import logging
import random

load_dotenv()

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='scraper.log',
                    filemode='w')



def test_link(driver):
    test_link = os.getenv("TEST_LINK")

    driver.get(test_link)

    old_data = driver.find_element(By.TAG_NAME, "body").text
    data = json.loads(old_data)
    print(data)
    return data

def get_term_from_offerings(data):
    try:
        term = data["course_details"]["offerings"][0]["open_terms"][0]["strm"].strip()
        print(f"Extracted term: {term}")
        return term
    except (IndexError, KeyError) as e:
        print(f"Failed to extract term due to an error: {e}")
        print(f"Data received was: {json.dumps(data, indent=4)}")
        return None

# def test_casaa():
#     driver = None
#     db = SessionLocal()

#     try:
#         clear_database(db)
#         driver = user_profile.create_driver()
#         browser = login.Browser(driver)
#         scraper = Scraper(browser)

#         major = "CASAA"
#         courses = scraper.get_courses_from_major(major)['courses'][:5]
#         logging.info(f"Retrieved {len(courses)} courses for CASAA")

#         for course_data in courses:
#             try:
#                 process_course(course_data, db, major, scraper)
#             except Exception as e:
#                 logging.error(f"Error processing course {course_data.get('catalog_nbr')}: {str(e)}")

#     except Exception as e:
#         logging.error(f"Error in test_casaa: {str(e)}")
#     finally:
#         if db:
#             db.close()
#         if driver:
#             driver.quit()

# def test_cascs():
    driver = None
    db = SessionLocal()

    try:
        driver = user_profile.create_driver()
        browser = login.Browser(driver)
        scraper = Scraper(browser)

        major = "CASCS"
        courses = scraper.get_courses_from_major(major)['courses'][:5]
        logging.info(f"Retrieved {len(courses)} courses for CASCS")

        for course_data in courses:
            try:
                process_course(course_data, db, major, scraper)
            except Exception as e:
                logging.error(f"Error processing course {course_data.get('catalog_nbr')}: {str(e)}")

    except Exception as e:
        logging.error(f"Error in test_cascs: {str(e)}")
    finally:
        if db:
            db.close()
        if driver:
            driver.quit()


# def main():
#     # use profile
#     driver = user_profile.create_driver()
#     browser = login.Browser(driver)
#     scraper = Scraper(browser)

#     # login.py
#     # browser.login_bu(os.getenv("TEST_LINK") ,os.getenv('USERNAME'), os.getenv('PASSWORD'))

#     # get data
#     majors = scraper.get_all_majors()
#     print(majors)

#     all_course_data = []
#     course_count = 0
#     max_courses = 30

#     for major in majors['subjects']:
#         print(f"working on {major['subject']}")

#         if course_count >= max_courses:
#             break

#         courses = scraper.get_courses_from_major(major['subject'])
#         for course in courses['courses']:
#             comp_details = scraper.get_complementary_details(course['crse_id'], course['effdt'], major['subject'], course['catalog_nbr'].strip(), course['typ_offr'])
#             print("Received complementary details:", comp_details)

#             course_data = {
#                 'complementary_details': comp_details
#             }
#             term = None
            
#             if 'offerings' in comp_details and any('open_terms' in offering for offering in comp_details['offerings']):
#                 for offering in comp_details['offerings']:
#                     if 'open_terms' in offering and offering['open_terms']:
#                         term = offering['open_terms'][0]['strm']
#                         detailed_info = scraper.get_course_details(course['crse_id'], term, offering['crse_offer_nbr'])
#                         course_data['detailed_info'] = detailed_info
#                         break
#             if term is not None:
#                 course_details = scraper.get_course_details(course['crse_id'], term, course['crse_offer_nbr'])
#                 course_data['course_details'] = course_details
#                 print(course_details)
#             else:
#                 print(f"No valid term found for course {course['catalog_nbr']}.")

#             all_course_data.append(course_data)
#             course_count += 1
#             if course_count >= max_courses:
#                 break

#             time.sleep(10)

#     # close after
#     driver.quit()
#     return all_course_data

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
    courses = scraper.get_courses_from_major(major)['courses'][:5]
    logging.info(f"Retrieved {len(courses)} courses for CASAA")

    for course_data in courses:
        try:
            process_course(course_data, db, major, scraper)
        except Exception as e:
            logging.error(f"Error processing CASAA course {course_data.get('catalog_nbr')}: {str(e)}")

def test_cascs(scraper, db):
    major = "CASCS"
    courses = scraper.get_courses_from_major(major)['courses'][:5]
    logging.info(f"Retrieved {len(courses)} courses for CASCS")

    for course_data in courses:
        try:
            process_course(course_data, db, major, scraper)
        except Exception as e:
            logging.error(f"Error processing CASCS course {course_data.get('catalog_nbr')}: {str(e)}")

def main():
    driver = None
    db = SessionLocal()

    try:
        clear_database(db)
        driver = user_profile.create_driver()
        browser = login.Browser(driver)
        scraper = Scraper(browser)

        majors = scraper.get_all_majors()
        logging.info(f"Retrieved {len(majors['subjects'])} majors")

        for major in majors['subjects']:
            # add slicing to test less majors
            major_code = major['subject']
            logging.info(f"Processing major: {major_code}")

            try:
                courses = scraper.get_courses_from_major(major_code)['courses']
                logging.info(f"Retrieved {len(courses)} courses for {major_code}")

                for course_data in courses:
                    try:
                        process_course(course_data, db, major_code, scraper)
                    except Exception as e:
                        logging.error(f"Error processing course {course_data.get('catalog_nbr')} in {major_code}: {str(e)}")

                logging.info(f"Finished processing all courses for {major_code}")
            except Exception as e:
                logging.error(f"Error processing major {major_code}: {str(e)}")

            time.sleep(5)

        logging.info("Finished processing all majors and courses")

    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
    finally:
        if db:
            db.close()
        if driver:
            driver.quit()

if __name__ == "__main__":
    # login initial from login.py
    # login.main()
    # test_link()
    # run_tests()

    main()
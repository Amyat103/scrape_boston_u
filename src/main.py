import requests
import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import login
import user_profile
import json
from scraper import Scraper
import time
from models import SessionLocal, Course, Section
from contextlib import contextmanager
from process import safe_extract, process_course


load_dotenv()

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

def test_cascs():
    driver = None
    db = None

    try:
        driver = user_profile.create_driver()
        browser = login.Browser(driver)
        scraper = Scraper(browser)

        major = "CASCS"
        courses = scraper.get_courses_from_major(major)['courses'][:5]
        print("Courses data structure:", courses)
        
        db = SessionLocal()
        for course_data in courses['courses']:
            comp_details = scraper.get_complementary_details(course_data['crse_id'], course_data['effdt'], major, course_data['catalog_nbr'].strip(), course_data['typ_offr'])
            print("Received complementary details:", comp_details) 

            course = Course(
                term=comp_details['effdt'],
                major=major,
                course_number=course_data['catalog_nbr'],
                full_title=comp_details['course_title'],
                description=comp_details['descrlong'],
                has_details=True if comp_details else False
            )
            db.add(course)

            if 'sections' in comp_details:
                for sec in comp_details['sections']:
                    section = Section(
                        course=course,
                        class_section=sec['class_section'],
                        class_type=sec['component'],
                        professor_name=sec['instructors'][0]['name'] if sec['instructors'] else None,
                        class_capacity=sec['class_capacity'],
                        enrollment_total=sec['enrollment_total'],
                        enrollment_available=sec['enrollment_available'],
                        days=sec['meetings'][0]['days'],
                        start_time=sec['meetings'][0]['start_time'],
                        end_time=sec['meetings'][0]['end_time'],
                        location=sec['meetings'][0]['facility_descr']
                    )
                    db.add(section)

            db.commit()

            time.sleep(10)

        driver.quit()
        
    except Exception as e:
        print(f"Error in cascs {e}")
        db.rollback()

    finally:
        db.close()
        driver.quit()

def test_casaa():
    driver = None
    db = None

    try:
        driver = user_profile.create_driver()
        browser = login.Browser(driver)
        scraper = Scraper(browser)

        major = "CASAA"
        courses = scraper.get_courses_from_major(major)['courses'][:5]
        print("Courses data structure:", courses)
        
        db = SessionLocal()
        for course_data in courses['courses']:
            comp_details = scraper.get_complementary_details(course_data['crse_id'], course_data['effdt'], major, course_data['catalog_nbr'].strip(), course_data['typ_offr'])
            print("Received complementary details:", comp_details) 

            course = Course(
                term=comp_details['effdt'],
                major=major,
                course_number=course_data['catalog_nbr'],
                full_title=comp_details['course_title'],
                description=comp_details['descrlong'],
                has_details=True if comp_details else False
            )
            db.add(course)

            if 'sections' in comp_details:
                for sec in comp_details['sections']:
                    section = Section(
                        course=course,
                        class_section=sec['class_section'],
                        class_type=sec['component'],
                        professor_name=sec['instructors'][0]['name'] if sec['instructors'] else None,
                        class_capacity=sec['class_capacity'],
                        enrollment_total=sec['enrollment_total'],
                        enrollment_available=sec['enrollment_available'],
                        days=sec['meetings'][0]['days'],
                        start_time=sec['meetings'][0]['start_time'],
                        end_time=sec['meetings'][0]['end_time'],
                        location=sec['meetings'][0]['facility_descr']
                    )
                    db.add(section)

            db.commit()

            time.sleep(10)

        driver.quit()
    
    except Exception as e:
        print(f"Error in casaa {e}")
        db.rollback()

    finally:
        db.close()
        driver.quit()


def main():
    # use profile
    driver = user_profile.create_driver()
    browser = login.Browser(driver)
    scraper = Scraper(browser)

    # login.py
    # browser.login_bu(os.getenv("TEST_LINK") ,os.getenv('USERNAME'), os.getenv('PASSWORD'))

    # get data
    majors = scraper.get_all_majors()
    print(majors)

    all_course_data = []
    course_count = 0
    max_courses = 30

    for major in majors['subjects']:
        print(f"working on {major['subject']}")

        if course_count >= max_courses:
            break

        courses = scraper.get_courses_from_major(major['subject'])
        for course in courses['courses']:
            comp_details = scraper.get_complementary_details(course['crse_id'], course['effdt'], major['subject'], course['catalog_nbr'].strip(), course['typ_offr'])
            print("Received complementary details:", comp_details)

            course_data = {
                'complementary_details': comp_details
            }
            term = None
            
            if 'offerings' in comp_details and any('open_terms' in offering for offering in comp_details['offerings']):
                for offering in comp_details['offerings']:
                    if 'open_terms' in offering and offering['open_terms']:
                        term = offering['open_terms'][0]['strm']
                        detailed_info = scraper.get_course_details(course['crse_id'], term, offering['crse_offer_nbr'])
                        course_data['detailed_info'] = detailed_info
                        break
            if term is not None:
                course_details = scraper.get_course_details(course['crse_id'], term, course['crse_offer_nbr'])
                course_data['course_details'] = course_details
                print(course_details)
            else:
                print(f"No valid term found for course {course['catalog_nbr']}.")

            all_course_data.append(course_data)
            course_count += 1
            if course_count >= max_courses:
                break

            time.sleep(10)

    # close after
    driver.quit()
    return all_course_data

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    # login initial from login.py
    # login.main()
    # test_link()
    
    test_casaa()
    test_cascs()



    # ONLY FOR TEST CASCS
    # ONLY FOR CASCS
    # combined_data = []
    #   # Run the test 20 times
    # data = test_cascs()
    # combined_data.extend(data)

    # with open("/Users/david/repos/scrape_boston_u/src/test.json", 'w', encoding='utf-8') as f:
    #     json.dump(data, f, ensure_ascii=False, indent=4)




# SOME CLASS DONT HAVE OFFERING
            # if 'offerings' in comp_details and comp_details['offerings']:
            #     offerings = comp_details['offerings'][0]
            #     if 'open_terms' in offerings and offerings['open_terms']:
            #         term = offerings['open_terms'][0].get('strm', '2248')
            #     else:
            #         term = '2248'
            #         print(f"No valid term found for course {course['catalog_nbr']}. Using default term.")
            # else:
            #     term = '2248'
            #     print(f"No offerings found for course {course['catalog_nbr']}. Using default term.")
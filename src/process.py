import json
import logging
from datetime import datetime, time

import psycopg2
from sqlalchemy.sql import func

from models import Course, Section
from scraper import Scraper


def convert_time(time_str):
    if time_str:
        try:
            time_parts = time_str.split(".")
            hours = int(time_parts[0])
            minutes = int(time_parts[1])

            time_obj = datetime.strptime(f"{hours:02d}:{minutes:02d}", "%H:%M")
            return time_obj.strftime("%I:%M %p").lower().lstrip("0")
        except (ValueError, IndexError) as e:
            print(f"Failed to parse time: {time_str}. Error: {e}")
            return None
    return None


def process_log_and_update_db(log_path, db_connection_string):
    try:
        conn = psycopg2.connect(db_connection_string)
        cur = conn.cursor()

        with open(log_path, "r") as file:
            for line in file:
                datetime_str = line.split(" - ")[0]
                datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S,%f")
                formatted_time = datetime_obj.strftime("%I:%M%p").lower()

                cur.execute(
                    "INSERT INTO your_table (time_column) VALUES (%s)",
                    (formatted_time,),
                )
                logging.info(f"Inserted time {formatted_time} into database.")

        conn.commit()
        cur.close()
        conn.close()
        logging.info("Database operations completed successfully.")

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"Error while connecting to PostgreSQL: {error}")
    finally:
        if conn is not None:
            conn.close()
            logging.info("Database connection is closed.")


def safe_extract(data, key, default=None):
    return data.get(key, default) if data else default


def process_course(course_data, major, scraper):
    try:
        effdt = safe_extract(course_data, "effdt")
        crse_id = safe_extract(course_data, "crse_id")
        catalog_nbr = safe_extract(course_data, "catalog_nbr", "").strip()
        typ_offr = safe_extract(course_data, "typ_offr")

        print(f"\n{'='*50}")
        print(f"Processing course: {major} {catalog_nbr} (ID: {crse_id})")
        print(f"Course data: effdt={effdt}, typ_offr={typ_offr}")
        print(f"{'='*50}\n")

        print(
            f">>> About to call get_complementary_details for {major} {catalog_nbr} <<<"
        )
        try:
            comp_details = scraper.get_complementary_details(
                crse_id, effdt, major, catalog_nbr, typ_offr
            )
            print(
                f">>> Finished get_complementary_details for {major} {catalog_nbr} <<<"
            )
            print(f"Complementary details: {json.dumps(comp_details, indent=2)}")
        except Exception as e:
            print(
                f"Error in get_complementary_details for {major} {catalog_nbr}: {str(e)}"
            )
            comp_details = {}

        course_details = comp_details.get("course_details", {})

        short_title = f"{major[-2:]}{catalog_nbr}"

        is_registerable = False
        term = None
        if course_details.get("offerings"):
            for offering in course_details["offerings"]:
                if offering.get("open_terms"):
                    is_registerable = True
                    term = offering["open_terms"][0]["strm"]
                    break

<<<<<<< HEAD
=======
        units = str(course_details.get("units_minimum", ""))

        hub_attributes = []
        for attr in course_details.get("attributes", []):
            if attr.get("crse_attribute") == "HUB":
                hub_value = attr.get("crse_attribute_value_descr", "")
                if hub_value.startswith("HUB "):
                    hub_attributes.append(hub_value[4:])

        if existing_course:
            existing_course.term = term
            existing_course.full_title = course_details.get("course_title")
            existing_course.description = course_details.get("descrlong")
            existing_course.has_details = bool(course_details)
            existing_course.is_registerable = is_registerable
            existing_course.short_title = short_title
            existing_course.hub_attributes = json.dumps(hub_attributes)
            existing_course.units = units
            existing_course.updated_at = func.now()
            logging.info(f"Updated existing course: {major} {catalog_nbr}")
        else:
            new_course = Course(
                term=term,
                major=major,
                course_number=catalog_nbr,
                full_title=course_details.get("course_title"),
                description=course_details.get("descrlong"),
                has_details=bool(course_details),
                is_registerable=is_registerable,
                short_title=short_title,
                hub_attributes=json.dumps(hub_attributes),
                units=units,
            )
            db.add(new_course)
            db.flush()
            existing_course = new_course
            logging.info(f"Added new course: {major} {catalog_nbr}")

>>>>>>> a4f1fcb (Revert "update scraping for new columns")
        sections = []
        if term:
            try:
                print(
                    f">>> About to call get_course_details for {major} {catalog_nbr} <<<"
                )
                detailed_info = scraper.get_course_details(crse_id, term, "1")
                print(f">>> Finished get_course_details for {major} {catalog_nbr} <<<")
                print(f"Course details: {json.dumps(detailed_info, indent=2)}")
                sections = detailed_info.get("sections", [])
            except Exception as e:
                print(f"Error processing sections for course {crse_id}: {str(e)}")
        else:
            print(f"No term found for {major} {catalog_nbr}, skipping course details")

        return {
            "major": major,
            "course_number": catalog_nbr,
            "term": term,
            "full_title": course_details.get("course_title"),
            "description": course_details.get("descrlong"),
            "has_details": bool(course_details),
            "is_registerable": is_registerable,
            "short_title": short_title,
            "hub_attributes": hub_attributes,
            "units": units,
            "sections": sections,
        }

    except Exception as e:
        print(f"Error processing course {crse_id} - {catalog_nbr}: {str(e)}")
        raise


def process_major(major_code, scraper, db):
    print(f"Starting to process major: {major_code}")
    courses = scraper.get_courses_from_major(major_code)["courses"]
    processed_course_numbers = set()

    for course_data in courses:
        try:
            processed_course = process_course(course_data, major_code, scraper)
            catalog_nbr = processed_course["course_number"]

            existing_course = (
                db.query(Course)
                .filter_by(course_number=catalog_nbr, major=major_code)
                .first()
            )

            if existing_course:
                for key, value in processed_course.items():
                    if key != "sections":
                        setattr(existing_course, key, value)
                print(f"Updated existing course: {major_code} {catalog_nbr}")
            else:
                new_course = Course(**processed_course)
                db.add(new_course)
                print(f"Added new course: {major_code} {catalog_nbr}")

            if processed_course["sections"]:
                db.query(Section).filter_by(course_id=existing_course.id).delete()
                for sec in processed_course["sections"]:
                    section = Section(
                        course_id=existing_course.id,
                        class_section=safe_extract(sec, "class_section"),
                        class_type=safe_extract(sec, "component"),
                        professor_name=safe_extract(sec, "instructors", [{}])[0].get(
                            "name"
                        ),
                        class_capacity=safe_extract(sec, "class_capacity", 0),
                        enrollment_total=safe_extract(sec, "enrollment_total", 0),
                        enrollment_available=safe_extract(
                            sec, "enrollment_available", 0
                        ),
                        days=safe_extract(sec, "meetings", [{}])[0].get("days"),
                        start_time=convert_time(
                            safe_extract(sec, "meetings", [{}])[0].get("start_time")
                        ),
                        end_time=convert_time(
                            safe_extract(sec, "meetings", [{}])[0].get("end_time")
                        ),
                        location=safe_extract(sec, "meetings", [{}])[0].get(
                            "facility_descr"
                        ),
                    )
                    db.add(section)
                    print(
                        f"Added section to database: {catalog_nbr} - {sec.get('class_section')}"
                    )
<<<<<<< HEAD

            processed_course_numbers.add(catalog_nbr)
        except Exception as e:
            print(f"Error processing course {course_data.get('catalog_nbr')}: {str(e)}")
=======
            except Exception as e:
                logging.error(
                    f"Error processing sections for course {crse_id}: {str(e)}"
                )

        db.commit()
        logging.info(f"Committed course {catalog_nbr} and its sections to database")
        return existing_course, sections
    except Exception as e:
        logging.error(f"Error processing course {crse_id} - {catalog_nbr}: {str(e)}")
        db.rollback()
        raise


def process_major(major_code, scraper, db):
    courses = scraper.get_courses_from_major(major_code)["courses"]
    processed_course_numbers = set()

    for course_data in courses:
        catalog_nbr = safe_extract(course_data, "catalog_nbr", "").strip()
        process_course(course_data, db, major_code, scraper)
        processed_course_numbers.add(catalog_nbr)
>>>>>>> a4f1fcb (Revert "update scraping for new columns")

    db_courses = db.query(Course).filter_by(major=major_code).all()
    for db_course in db_courses:
        if db_course.course_number not in processed_course_numbers:
            db_course.is_active = False
            print(f"Deactivated course: {major_code} {db_course.course_number}")

    db.commit()
    print(f"Finished processing major: {major_code}")

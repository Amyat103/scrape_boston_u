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


def process_course(course_data, db, major, scraper):
    try:
        effdt = safe_extract(course_data, "effdt")
        crse_id = safe_extract(course_data, "crse_id")
        catalog_nbr = safe_extract(course_data, "catalog_nbr", "").strip()
        typ_offr = safe_extract(course_data, "typ_offr")

        existing_course = (
            db.query(Course).filter_by(course_number=catalog_nbr, major=major).first()
        )

        logging.info(f"Processing course: {crse_id} - {catalog_nbr}")

        comp_details = scraper.get_complementary_details(
            crse_id, effdt, major, catalog_nbr, typ_offr
        )

        course_details = comp_details.get("course_details", {})
        hub_attributes = comp_details.get("processed_hub_attributes", [])
        units = comp_details.get("processed_units", "")

        short_title = f"{major[-2:]}{catalog_nbr}"

        is_registerable = False
        if course_details.get("offerings"):
            for offering in course_details["offerings"]:
                if offering.get("open_terms"):
                    is_registerable = True
                    break

        term = None
        if course_details.get("offerings"):
            for offering in course_details["offerings"]:
                if offering.get("open_terms"):
                    term = offering["open_terms"][0]["strm"]
                    break

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

        sections = []
        if term:
            try:
                db.query(Section).filter_by(course_id=existing_course.id).delete()

                detailed_info = scraper.get_course_details(crse_id, term, "1")
                sections = detailed_info.get("sections", [])

                for sec in sections:
                    start_time_raw = safe_extract(sec, "meetings", [{}])[0].get(
                        "start_time"
                    )
                    end_time_raw = safe_extract(sec, "meetings", [{}])[0].get(
                        "end_time"
                    )
                    start_time = convert_time(start_time_raw)
                    end_time = convert_time(end_time_raw)

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
                        start_time=start_time,
                        end_time=end_time,
                        location=safe_extract(sec, "meetings", [{}])[0].get(
                            "facility_descr"
                        ),
                    )
                    db.add(section)
                    logging.info(
                        f"Added section to database: {catalog_nbr} - {sec.get('class_section')} (Start: {start_time}, End: {end_time})"
                    )

                if sections:
                    units_from_sections = sections[0].get("units")
                    if units_from_sections and units_from_sections != units:
                        logging.warning(
                            f"Units mismatch for {major} {catalog_nbr}: {units} vs {units_from_sections}"
                        )
                    units = units_from_sections or units
                    existing_course.units = units
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

    db_courses = db.query(Course).filter_by(major=major_code).all()
    for db_course in db_courses:
        if db_course.course_number not in processed_course_numbers:
            db_course.is_active = False
            logging.info(f"Deactivated course: {major_code} {db_course.course_number}")

    db.commit()

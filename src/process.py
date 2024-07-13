from models import Course, Section
from scraper import Scraper
import logging
import json
from datetime import datetime

def convert_time(time_str):
    if time_str:
        try:
            time_obj = datetime.strptime(time_str.split('.')[0], '%H.%M.%S')
            return time_obj.time()
        except ValueError:
            return None
    return None


def safe_extract(data, key, default=None):
    return data.get(key, default) if data else default

def process_course(course_data, db, major, scraper):
    try:
        effdt = safe_extract(course_data, 'effdt')
        crse_id = safe_extract(course_data, 'crse_id')
        catalog_nbr = safe_extract(course_data, 'catalog_nbr', '').strip()
        typ_offr = safe_extract(course_data, 'typ_offr')

        logging.info(f"Processing course: {crse_id} - {catalog_nbr}")

        comp_details = scraper.get_complementary_details(crse_id, effdt, major, catalog_nbr, typ_offr)
        logging.info(f"Complementary details for {crse_id}: {json.dumps(comp_details, indent=2)}")

        course_details = comp_details.get('course_details', {})
        
        short_title = f"{major[-2:]}{catalog_nbr}"

        is_registerable = False
        if course_details.get('offerings'):
            for offering in course_details['offerings']:
                if offering.get('open_terms'):
                    is_registerable = True
                    break
        
        term = None
        if course_details.get('offerings'):
            for offering in course_details['offerings']:
                if offering.get('open_terms'):
                    term = offering['open_terms'][0]['strm']
                    break

        course = Course(
            term=course_details.get('effdt'),
            major=major,
            course_number=catalog_nbr,
            full_title=course_details.get('course_title'),
            description=course_details.get('descrlong'),
            has_details=bool(comp_details),
            is_registerable=is_registerable,
            short_title=short_title
        )
        db.add(course)
        logging.info(f"Added course to database: {catalog_nbr}")

        sections = []
        if term:
            try:
                detailed_info = scraper.get_course_details(crse_id, term, "1")
                sections = detailed_info.get('sections', [])
            except Exception as e:
                logging.error(f"Error fetching detailed info for course {crse_id}: {str(e)}")

        logging.info(f"Sections for {catalog_nbr}: {json.dumps(sections, indent=2)}")

        for sec in sections:
            start_time = convert_time(safe_extract(sec, 'meetings', [{}])[0].get('start_time'))
            end_time = convert_time(safe_extract(sec, 'meetings', [{}])[0].get('end_time'))
            
            section = Section(
                course=course,
                class_section=safe_extract(sec, 'class_section'),
                class_type=safe_extract(sec, 'component'),
                professor_name=safe_extract(sec, 'instructors', [{}])[0].get('name'),
                class_capacity=safe_extract(sec, 'class_capacity', 0),
                enrollment_total=safe_extract(sec, 'enrollment_total', 0),
                enrollment_available=safe_extract(sec, 'enrollment_available', 0),
                days=safe_extract(sec, 'meetings', [{}])[0].get('days'),
                start_time=start_time,
                end_time=end_time,
                location=safe_extract(sec, 'meetings', [{}])[0].get('facility_descr')
            )
            db.add(section)
            logging.info(f"Added section to database: {catalog_nbr} - {sec.get('class_section')} (Start: {start_time}, End: {end_time})")

        db.commit()
        logging.info(f"Committed course {catalog_nbr} and its sections to database")
    except Exception as e:
        logging.error(f"Error processing course {crse_id}: {str(e)}")
        db.rollback()
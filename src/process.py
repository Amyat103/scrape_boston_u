from models import Course, Section
from scraper import Scraper


def safe_extract(data, key, default=None):
    return data.get(key, default) if data else default

def process_course(course_data, db, major):
    crse_id = safe_extract(course_data, 'crse_id')
    effdt = safe_extract(course_data, 'effdt')
    catalog_nbr = safe_extract(course_data, 'catalog_nbr', '').strip()
    typ_offr = safe_extract(course_data, 'typ_offr')

    comp_details = self.scraper.get_complementary_details(crse_id, effdt, major, catalog_nbr, typ_offr)
    print("Received complementary details:", comp_details)

    course = Course(
        term=comp_details['effdt'],
        major=major,
        course_number=catalog_nbr,
        full_title=comp_details['course_title'],
        description=comp_details['descrlong'],
        has_details=bool(comp_details)
    )
    db.add(course)

    sections = safe_extract(comp_details, 'sections', [])
    for sec in sections:
        section = Section(
            course=course,
            class_section=safe_extract(sec, 'class_section'),
            class_type=safe_extract(sec, 'component'),
            professor_name=safe_extract(sec, 'instructors', [{}])[0].get('name'),
            class_capacity=safe_extract(sec, 'class_capacity', 0),
            enrollment_total=safe_extract(sec, 'enrollment_total', 0),
            enrollment_available=safe_extract(sec, 'enrollment_available', 0),
            days=safe_extract(sec, 'meetings', [{}])[0].get('days'),
            start_time=safe_extract(sec, 'meetings', [{}])[0].get('start_time'),
            end_time=safe_extract(sec, 'meetings', [{}])[0].get('end_time'),
            location=safe_extract(sec, 'meetings', [{}])[0].get('facility_descr')
        )
        db.add(section)

    db.commit()
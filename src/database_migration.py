import argparse
import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from models import Base

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()


def create_db_engine(url):
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            pass
        return engine
    except OperationalError:
        return None


def column_exists(engine, table_name, column_name):
    with engine.connect() as connection:
        query = text(
            f"""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name=:table AND column_name=:column
            );
        """
        )
        result = connection.execute(query, {"table": table_name, "column": column_name})
        return result.scalar()


def migrate(database_url=None):
    if not database_url:
        database_url = os.getenv("DB_URL")
        engine = create_db_engine(database_url)

        if engine is None:
            logger.info("Private connection failed. Trying public connection.")
            database_url = os.getenv("DB_PUBLIC")
            engine = create_db_engine(database_url)

        if engine is None:
            logger.error("Both private and public connections failed.")
            return
    else:
        engine = create_db_engine(database_url)

    logger.info(f"Successfully connected to database")

    try:
        Base.metadata.create_all(engine)

        with engine.begin() as connection:
            if not column_exists(engine, "courses", "hub_attributes"):
                connection.execute(
                    text("ALTER TABLE courses ADD COLUMN hub_attributes JSON")
                )
            if not column_exists(engine, "courses", "units"):
                connection.execute(
                    text("ALTER TABLE courses ADD COLUMN units VARCHAR(10)")
                )

        with engine.begin() as connection:
            if not column_exists(engine, "sections", "professor_overall_quality"):
                connection.execute(
                    text(
                        "ALTER TABLE sections ADD COLUMN professor_overall_quality FLOAT"
                    )
                )
            if not column_exists(engine, "sections", "professor_difficulty"):
                connection.execute(
                    text("ALTER TABLE sections ADD COLUMN professor_difficulty FLOAT")
                )
            if not column_exists(engine, "sections", "professor_link"):
                connection.execute(
                    text("ALTER TABLE sections ADD COLUMN professor_link VARCHAR(255)")
                )
            if not column_exists(engine, "sections", "last_rmp_update"):
                connection.execute(
                    text("ALTER TABLE sections ADD COLUMN last_rmp_update TIMESTAMP")
                )

        logger.info("Migration completed successfully.")
    except SQLAlchemyError as e:
        logger.error(f"An error occurred during migration: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run database migrations")
    parser.add_argument("--db_url", help="Database URL (overrides .env file)")
    args = parser.parse_args()

    migrate(args.db_url)

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = (
    f"postgresql://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@"
    f"{os.getenv('PGHOST')}:{os.getenv('PGPORT')}/{os.getenv('PGDATABASE')}"
)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def test_db_connection():
    session = Session()
    try:
        result = session.execute(text("SELECT 1"))
        print("Connection Test Result:", result.fetchall())
    except Exception as e:
        print("Error during database operation:", e)
    finally:
        session.close()


if __name__ == "__main__":
    test_db_connection()

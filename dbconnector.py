from sqlalchemy import create_engine
from urllib.parse import quote_plus

def get_engine():
    password = quote_plus("1234")

    DATABASE_URL = f"postgresql+psycopg2://postgres:{password}@localhost:5432/Retail_Sales"

    engine = create_engine(DATABASE_URL)

    return engine
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        "postgresql://postgres:Vivek%402006@localhost:5432/bank",
        cursor_factory=RealDictCursor
    )

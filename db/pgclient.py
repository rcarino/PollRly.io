import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect("dbname='pollr' host='localhost'", cursor_factory=RealDictCursor)
cur = conn.cursor()


def query(q, vars=None):
    cur.execute(q, vars=vars)
    return cur.fetchall()


def query_one(q, vars=None):
    execute(q, vars=vars)
    return cur.fetchone()


def execute(q, vars=None):
    cur.execute(q, vars=vars)
    conn.commit()

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(database=os.getenv('NAME'),
                        user=os.getenv('USER'),
                        host=os.getenv('HOST'),
                        password=os.getenv('PASSWORD'),
                        port=os.getenv('PORT'))

cur = conn.cursor()

create_table_query = '''
CREATE TABLE IF NOT EXISTS linkedin_jobs (
    id SERIAL PRIMARY KEY,
    email VARCHAR(254) NOT NULL,
    skills TEXT,
    linkedin_profile_link TEXT,
    post_profile TEXT NOT NULL,
    post_content TEXT NOT NULL,
    urn_id TEXT UNIQUE
);
'''

cur.execute(create_table_query)
conn.commit()
cur.close()
conn.close()

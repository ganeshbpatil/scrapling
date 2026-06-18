import os
try:
    import psycopg2
    from psycopg2.extras import execute_values
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

INSERT_SQL = """
INSERT INTO leads (name, phone, email, configuration, location_interest,
    budget, lead_source, source_url, lead_date, intent, confidence_score, inquiry_text)
VALUES %s ON CONFLICT (email, phone) DO NOTHING
"""

class PostgresStorage:
    def __init__(self, dsn: str = None):
        if not HAS_PSYCOPG2:
            raise RuntimeError("psycopg2 not installed")
        dsn = dsn or os.getenv("POSTGRES_DSN", "postgresql://postgres:secret@localhost:5432/pune_leads")
        self.conn = psycopg2.connect(dsn)

    def save(self, lead: dict):
        with self.conn.cursor() as cur:
            execute_values(cur, INSERT_SQL, [(
                lead.get("name"), lead.get("phone"), lead.get("email"),
                lead.get("configuration"), lead.get("location_interest"),
                lead.get("budget"), lead.get("lead_source"), lead.get("source_url"),
                lead.get("lead_date"), lead.get("intent"), lead.get("confidence_score"),
                lead.get("inquiry_text"),
            )])
        self.conn.commit()

    def close(self):
        self.conn.close()

CREATE TABLE IF NOT EXISTS leads (
    id               SERIAL PRIMARY KEY,
    name             VARCHAR(255),
    phone            VARCHAR(20),
    email            VARCHAR(255),
    configuration    VARCHAR(50),
    location_interest VARCHAR(100),
    budget           VARCHAR(100),
    lead_source      VARCHAR(100),
    source_url       TEXT,
    lead_date        DATE,
    inquiry_text     TEXT,
    confidence_score FLOAT DEFAULT 0.0,
    intent           VARCHAR(100),
    created_at       TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_lead UNIQUE (email, phone)
);
CREATE INDEX IF NOT EXISTS idx_leads_phone         ON leads(phone);
CREATE INDEX IF NOT EXISTS idx_leads_email         ON leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_location      ON leads(location_interest);
CREATE INDEX IF NOT EXISTS idx_leads_configuration ON leads(configuration);
CREATE INDEX IF NOT EXISTS idx_leads_lead_source   ON leads(lead_source);
CREATE INDEX IF NOT EXISTS idx_leads_lead_date     ON leads(lead_date);
CREATE INDEX IF NOT EXISTS idx_leads_intent        ON leads(intent);

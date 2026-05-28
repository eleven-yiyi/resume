CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Parsed resume facts
CREATE TABLE IF NOT EXISTS resumes (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  raw_text    TEXT NOT NULL,
  parsed_json JSONB NOT NULL DEFAULT '{}',
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- User preference slots (5 core + soft constraints)
CREATE TABLE IF NOT EXISTS preferences (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resume_id         UUID REFERENCES resumes(id) ON DELETE CASCADE,
  job_functions     TEXT[]   DEFAULT '{}',   -- jf
  work_arrangement  TEXT,                    -- wa: onsite|hybrid|remote|open
  location          TEXT,                    -- loc
  job_type          TEXT,                    -- jt: full-time|part-time|contract|internship
  salary_min        INTEGER,                 -- sal
  salary_max        INTEGER,
  salary_negotiable BOOLEAN  DEFAULT FALSE,
  extra_notes       JSONB    DEFAULT '[]',   -- free-text soft constraints from chat
  feedback_reasons  JSONB    DEFAULT '[]',   -- dislike reasons from Page 3
  created_at        TIMESTAMPTZ DEFAULT NOW()
);

-- Southeast Asia job descriptions
CREATE TABLE IF NOT EXISTS job_descriptions (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title            TEXT    NOT NULL,
  company          TEXT    NOT NULL,
  location         TEXT    NOT NULL,          -- city, country
  work_arrangement TEXT,                      -- onsite|hybrid|remote
  job_type         TEXT    DEFAULT 'full-time',
  salary_min       INTEGER,
  salary_max       INTEGER,
  currency         TEXT    DEFAULT 'SGD',
  description      TEXT    NOT NULL,
  highlights       JSONB   DEFAULT '[]',      -- 3-5 bullet strings
  tags             JSONB   DEFAULT '[]',      -- skill/domain tags
  embedding        vector(384),               -- all-MiniLM-L6-v2
  created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Like / dislike signals (stored for future recall bias)
CREATE TABLE IF NOT EXISTS match_feedback (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resume_id  UUID REFERENCES resumes(id) ON DELETE CASCADE,
  jd_id      UUID REFERENCES job_descriptions(id) ON DELETE CASCADE,
  action     TEXT NOT NULL CHECK (action IN ('like', 'dislike')),
  reason     TEXT,                            -- populated on dislike
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector index (100 JDs → lists=5 is fine)
CREATE INDEX IF NOT EXISTS jd_embedding_idx
  ON job_descriptions USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 5);

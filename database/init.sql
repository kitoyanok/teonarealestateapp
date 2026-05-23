-- Этот файл создает структуру базы данных PostgreSQL.
-- Проще говоря: здесь перечислены таблицы, связи между ними и базовые ограничения на данные.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  login VARCHAR(120) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name VARCHAR(160) NOT NULL DEFAULT 'Риелтор',
  email VARCHAR(160),
  phone VARCHAR(40),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  realtor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(160) NOT NULL,
  phone VARCHAR(40) NOT NULL,
  email VARCHAR(160),
  send_channel VARCHAR(40) NOT NULL DEFAULT 'copy',
  send_contact VARCHAR(200),
  status VARCHAR(40) NOT NULL DEFAULT 'new',
  property_type VARCHAR(20) NOT NULL CHECK (property_type IN ('apartment', 'house')),
  comment TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS client_search_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID UNIQUE NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  budget_min NUMERIC,
  budget_max NUMERIC,
  rooms_min INTEGER,
  rooms_max INTEGER,
  area_min NUMERIC,
  area_max NUMERIC,
  districts TEXT[] NOT NULL DEFAULT '{}',
  settlement_names TEXT[] NOT NULL DEFAULT '{}',
  completion_year_min INTEGER,
  completion_year_max INTEGER,
  finishing VARCHAR(80),
  floor_min INTEGER,
  floor_max INTEGER,
  house_area_min NUMERIC,
  house_area_max NUMERIC,
  land_area_min NUMERIC,
  land_area_max NUMERIC,
  floors_count_min INTEGER,
  floors_count_max INTEGER,
  bedrooms_min INTEGER,
  bedrooms_max INTEGER,
  house_material VARCHAR(120),
  communications TEXT[] NOT NULL DEFAULT '{}',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS properties (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  external_id TEXT,
  source_name VARCHAR(160),
  source_url TEXT UNIQUE NOT NULL,
  property_type VARCHAR(20) NOT NULL CHECK (property_type IN ('apartment', 'house')),
  title TEXT NOT NULL,
  complex_name VARCHAR(240),
  developer_name VARCHAR(240),
  description TEXT,
  city VARCHAR(120),
  district VARCHAR(160),
  address TEXT,
  settlement_name VARCHAR(200),
  price NUMERIC,
  price_per_meter NUMERIC,
  area NUMERIC,
  rooms INTEGER,
  floor INTEGER,
  floors_total INTEGER,
  house_area NUMERIC,
  land_area NUMERIC,
  bedrooms INTEGER,
  house_floors INTEGER,
  house_material VARCHAR(120),
  communications TEXT[] NOT NULL DEFAULT '{}',
  completion_year INTEGER,
  finishing VARCHAR(120),
  images TEXT[] NOT NULL DEFAULT '{}',
  raw_data JSONB,
  first_seen_at TIMESTAMP NOT NULL DEFAULT NOW(),
  last_seen_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS client_found_properties (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  match_score INTEGER DEFAULT 0,
  match_reasons TEXT[] NOT NULL DEFAULT '{}',
  mismatch_reasons TEXT[] NOT NULL DEFAULT '{}',
  is_hidden BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE(client_id, property_id)
);

CREATE TABLE IF NOT EXISTS shortlist_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
  note TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE(client_id, property_id)
);

CREATE TABLE IF NOT EXISTS share_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  channel VARCHAR(40) NOT NULL DEFAULT 'copy',
  contact VARCHAR(200),
  message_text TEXT NOT NULL,
  copied_at TIMESTAMP,
  sent_marked_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS search_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  status VARCHAR(40) NOT NULL DEFAULT 'started',
  property_type VARCHAR(20) NOT NULL CHECK (property_type IN ('apartment', 'house')),
  total_found INTEGER NOT NULL DEFAULT 0,
  total_saved INTEGER NOT NULL DEFAULT 0,
  error_message TEXT,
  started_at TIMESTAMP NOT NULL DEFAULT NOW(),
  finished_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_clients_realtor_id ON clients(realtor_id);
CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status);
CREATE INDEX IF NOT EXISTS idx_properties_source_url ON properties(source_url);
CREATE INDEX IF NOT EXISTS idx_found_client_id ON client_found_properties(client_id);
CREATE INDEX IF NOT EXISTS idx_shortlist_client_id ON shortlist_items(client_id);
CREATE INDEX IF NOT EXISTS idx_search_runs_client_id ON search_runs(client_id);

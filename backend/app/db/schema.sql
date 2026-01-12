-- ============================
-- DATABASE SCHEMA: ProdOps AI
-- ============================
-- ============================
-- 1. USERS & ACCESS CONTROL
-- ============================
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  user_email VARCHAR(100) UNIQUE NOT NULL,
  full_name VARCHAR(100),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE roles (
  id SERIAL PRIMARY KEY,
  role_name VARCHAR(50) UNIQUE NOT NULL
);
CREATE TABLE user_roles (
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
  role_id INT REFERENCES roles(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, role_id)
);
-- ============================
-- 2. PLANT STRUCTURE
-- ============================
CREATE TABLE plants (
  id SERIAL PRIMARY KEY,
  plant_code VARCHAR(20) UNIQUE NOT NULL,
  plant_name VARCHAR(100),
  location VARCHAR(100),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE production_lines (
  id SERIAL PRIMARY KEY,
  line_code VARCHAR(20) UNIQUE NOT NULL,
  line_name VARCHAR(100),
  plant_id INT REFERENCES plants(id),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE machines (
  id SERIAL PRIMARY KEY,
  machine_code VARCHAR(30) UNIQUE NOT NULL,
  machine_name VARCHAR(100),
  line_id INT REFERENCES production_lines(id),
  machine_type VARCHAR(50),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ============================
-- 3. PRODUCTION DATA
-- ============================
CREATE TABLE production_log (
  id SERIAL PRIMARY KEY,
  line_id INT REFERENCES production_lines(id),
  machine_id INT REFERENCES machines(id),
  event_time TIMESTAMP NOT NULL,
  shift_code CHAR(1) CHECK (shift_code IN ('A', 'B', 'C')),
  quantity_good INT DEFAULT 0,
  quantity_reject INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ============================
-- 4. DOWNTIME EVENTS
-- ============================
CREATE TABLE downtime_log (
  id SERIAL PRIMARY KEY,
  line_id INT REFERENCES production_lines(id),
  machine_id INT REFERENCES machines(id),
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  reason_code VARCHAR(30),
  reason_text VARCHAR(200),
  category VARCHAR(50),
  -- Breakdown, Changeover, Planned
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ============================
-- 5. TICKETING SYSTEM
-- ============================
CREATE TABLE tickets (
  id SERIAL PRIMARY KEY,
  ticket_no VARCHAR(20) UNIQUE NOT NULL,
  ticket_type VARCHAR(30),
  -- Maintenance, NCR
  line_id INT REFERENCES production_lines(id),
  machine_id INT REFERENCES machines(id),
  issue_summary VARCHAR(300),
  severity VARCHAR(20),
  -- Low, Medium, High
  status VARCHAR(20),
  -- OPEN, IN_PROGRESS, CLOSED
  created_by INT REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE ticket_comments (
  id SERIAL PRIMARY KEY,
  ticket_id INT REFERENCES tickets(id) ON DELETE CASCADE,
  comment_text TEXT,
  commented_by INT REFERENCES users(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ============================
-- 6. NOTIFICATIONS
-- ============================
CREATE TABLE notification_config (
  id SERIAL PRIMARY KEY,
  role_id INT REFERENCES roles(id),
  severity VARCHAR(20),
  notify_email BOOLEAN DEFAULT TRUE,
  notify_whatsapp BOOLEAN DEFAULT TRUE
);
CREATE TABLE notification_logs (
  id SERIAL PRIMARY KEY,
  ticket_id INT REFERENCES tickets(id),
  channel VARCHAR(20),
  -- EMAIL, WHATSAPP
  recipient VARCHAR(100),
  status VARCHAR(20),
  -- SENT, FAILED
  sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ============================
-- 7. AI MEMORY & AUDIT
-- ============================
CREATE TABLE user_memory (
  user_id INT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  last_context TEXT,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE agent_audit_logs (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  user_query TEXT,
  tools_used TEXT,
  response_time_ms INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- ============================
-- 8. INDEXES (PERFORMANCE)
-- ============================
CREATE INDEX idx_prod_event_time ON production_log(event_time);
CREATE INDEX idx_downtime_start ON downtime_log(start_time);
CREATE INDEX idx_ticket_status ON tickets(status);
CREATE INDEX idx_ticket_severity ON tickets(severity);
CREATE INDEX idx_ticket_created_at ON tickets(created_at);
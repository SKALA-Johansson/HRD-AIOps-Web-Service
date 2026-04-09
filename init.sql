-- MariaDB bootstrap schema for SKALA mini project
-- NOTE: This script runs only on first container initialization
-- (when /var/lib/mysql volume is empty).

-- ---------------------------------------------------------------------
-- 1) Databases
-- ---------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS user_profile_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS goal_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS curriculum_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS learning_platform_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS tutor_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS report_growth_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS content_management_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS feedback_approval_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Compatibility aliases from older naming drafts
CREATE DATABASE IF NOT EXISTS goal_setter_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS ai_tutor_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 2) User/Profile domain
-- ---------------------------------------------------------------------
USE user_profile_db;

CREATE TABLE IF NOT EXISTS users (
  user_id CHAR(36) PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS profiles (
  profile_id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  department VARCHAR(100),
  job_role VARCHAR(100),
  resume_summary TEXT,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_profiles_user FOREIGN KEY (user_id) REFERENCES users(user_id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 3) Goal Setter Agent domain (active)
-- ---------------------------------------------------------------------
USE goal_db;

CREATE TABLE IF NOT EXISTS goals (
  id CHAR(36) PRIMARY KEY,
  employee_id VARCHAR(100) NOT NULL,
  employee_name VARCHAR(100) NOT NULL,
  department VARCHAR(100) NOT NULL,
  role VARCHAR(100) NOT NULL,
  career_level VARCHAR(50) NOT NULL,
  experience_years INT DEFAULT 0,
  skills TEXT NOT NULL,
  goals TEXT NULL,
  status ENUM('generating', 'draft', 'approved', 'rejected', 'error') NOT NULL DEFAULT 'draft',
  rejection_reason TEXT NULL,
  created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  INDEX idx_goals_employee_id (employee_id),
  INDEX idx_goals_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 4) Curriculum Designer Agent domain (active)
-- ---------------------------------------------------------------------
USE curriculum_db;

CREATE TABLE IF NOT EXISTS curriculums (
  id CHAR(36) PRIMARY KEY,
  goal_id VARCHAR(100) NOT NULL,
  employee_id VARCHAR(100) NOT NULL,
  employee_name VARCHAR(100) NOT NULL,
  department VARCHAR(100) NOT NULL,
  role VARCHAR(100) NOT NULL,
  career_level VARCHAR(50) NOT NULL,
  title VARCHAR(200) NOT NULL,
  description TEXT NULL,
  total_weeks INT DEFAULT 12,
  status ENUM('generating', 'draft', 'approved', 'rejected', 'revised', 'active', 'completed', 'error') NOT NULL DEFAULT 'draft',
  revision_note TEXT NULL,
  version INT DEFAULT 1,
  created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
  INDEX idx_curriculums_goal_id (goal_id),
  INDEX idx_curriculums_employee_id (employee_id),
  INDEX idx_curriculums_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS modules (
  id CHAR(36) PRIMARY KEY,
  curriculum_id CHAR(36) NOT NULL,
  week_number INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  description TEXT NULL,
  content TEXT NULL,
  learning_objectives TEXT NULL,
  resources TEXT NULL,
  assignments TEXT NULL,
  estimated_hours INT DEFAULT 8,
  created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  INDEX idx_modules_curriculum_id (curriculum_id),
  INDEX idx_modules_week_number (week_number),
  CONSTRAINT fk_modules_curriculum FOREIGN KEY (curriculum_id) REFERENCES curriculums(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 5) AI Tutor Agent domain (active)
-- ---------------------------------------------------------------------
USE tutor_db;

CREATE TABLE IF NOT EXISTS tutor_sessions (
  id CHAR(36) PRIMARY KEY,
  employee_id VARCHAR(100) NOT NULL,
  employee_name VARCHAR(100) NOT NULL,
  curriculum_id VARCHAR(100) NULL,
  module_id VARCHAR(100) NULL,
  module_title VARCHAR(200) NULL,
  session_type ENUM('chat', 'quiz', 'assignment') NOT NULL DEFAULT 'chat',
  messages TEXT NULL,
  status ENUM('active', 'completed', 'abandoned') NOT NULL DEFAULT 'active',
  started_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  ended_at DATETIME(6) NULL,
  INDEX idx_tutor_sessions_employee_id (employee_id),
  INDEX idx_tutor_sessions_curriculum_id (curriculum_id),
  INDEX idx_tutor_sessions_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS feedback (
  id CHAR(36) PRIMARY KEY,
  session_id CHAR(36) NOT NULL,
  employee_id VARCHAR(100) NOT NULL,
  feedback_type ENUM('quiz_grading', 'assignment_grading', 'growth_report', 'anomaly') NOT NULL,
  score FLOAT NULL,
  max_score FLOAT NULL,
  passed BOOLEAN NULL,
  summary TEXT NULL,
  strengths TEXT NULL,
  weaknesses TEXT NULL,
  recommendations TEXT NULL,
  detail TEXT NULL,
  is_anomaly BOOLEAN DEFAULT FALSE,
  anomaly_type VARCHAR(100) NULL,
  created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  INDEX idx_feedback_session_id (session_id),
  INDEX idx_feedback_employee_id (employee_id),
  CONSTRAINT fk_feedback_session FOREIGN KEY (session_id) REFERENCES tutor_sessions(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS learning_activities (
  id CHAR(36) PRIMARY KEY,
  employee_id VARCHAR(100) NOT NULL,
  session_id VARCHAR(100) NULL,
  activity_type VARCHAR(100) NOT NULL,
  module_id VARCHAR(100) NULL,
  score FLOAT NULL,
  duration_minutes INT NULL,
  `metadata` TEXT NULL,
  logged_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
  INDEX idx_learning_activities_employee_id (employee_id),
  INDEX idx_learning_activities_logged_at (logged_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- 6) Planned service domains (placeholder tables)
-- ---------------------------------------------------------------------
USE learning_platform_db;

CREATE TABLE IF NOT EXISTS learning_progress (
  progress_id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  module_id CHAR(36) NOT NULL,
  status VARCHAR(50) DEFAULT 'NOT_STARTED',
  completion_rate DECIMAL(5,2) DEFAULT 0.00,
  last_accessed_at TIMESTAMP NULL,
  INDEX idx_learning_progress_user_id (user_id),
  INDEX idx_learning_progress_module_id (module_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS assignments (
  assignment_id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  module_id CHAR(36) NOT NULL,
  submission_content TEXT,
  submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_assignments_user_id (user_id),
  INDEX idx_assignments_module_id (module_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

USE report_growth_db;

CREATE TABLE IF NOT EXISTS growth_reports (
  report_id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  report_period VARCHAR(50),
  strengths TEXT,
  weaknesses TEXT,
  mentoring_guide TEXT,
  generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_growth_reports_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

USE content_management_db;

CREATE TABLE IF NOT EXISTS contents (
  content_id CHAR(36) PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  content_type VARCHAR(50),
  s3_url VARCHAR(500),
  vector_db_collection_name VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

USE feedback_approval_db;

CREATE TABLE IF NOT EXISTS approvals (
  approval_id CHAR(36) PRIMARY KEY,
  target_type VARCHAR(50) COMMENT 'GOAL or CURRICULUM',
  target_id CHAR(36) NOT NULL,
  approver_id CHAR(36) NOT NULL,
  status VARCHAR(50) NOT NULL COMMENT 'APPROVED, REJECTED',
  comments TEXT,
  processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_approvals_target (target_type, target_id),
  INDEX idx_approvals_approver (approver_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

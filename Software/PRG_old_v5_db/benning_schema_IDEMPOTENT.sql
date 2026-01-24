-- ============================================================================
-- Benning Device Manager - Idempotentes Datenbankschema
-- ============================================================================
-- Dieses Schema kann mehrfach ausgeführt werden ohne Fehler
-- ANCHOR: DROP IF EXISTS statt DROP DATABASE

-- ANCHOR: Drop existing database (IF EXISTS verhindert Fehler)
DROP DATABASE IF EXISTS benning_device_manager;

-- ANCHOR: Create database
CREATE DATABASE benning_device_manager 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- ANCHOR: Use database
USE benning_device_manager;

-- ============================================================================
-- ANCHOR: Devices Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS devices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    serial_number VARCHAR(255) UNIQUE,
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    location VARCHAR(255),
    purchase_date DATE,
    last_inspection DATE,
    next_inspection DATE,
    status ENUM('active', 'inactive', 'maintenance', 'retired') DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_serial (serial_number),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- ANCHOR: Inspections Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS inspections (
    id INT PRIMARY KEY AUTO_INCREMENT,
    device_id INT NOT NULL,
    inspection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result ENUM('pass', 'fail', 'pending') DEFAULT 'pending',
    notes TEXT,
    inspector VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_device (device_id),
    INDEX idx_date (inspection_date),
    INDEX idx_result (result)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- ANCHOR: Users Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'inspector', 'viewer') DEFAULT 'viewer',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- ANCHOR: Audit Log Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(100),
    entity_type VARCHAR(100),
    entity_id INT,
    changes JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- ANCHOR: Verify Schema
-- ============================================================================
SHOW TABLES;
DESC devices;

-- ============================================================================
-- Datenbankschema erfolgreich erstellt (oder bereits vorhanden)!
-- ============================================================================

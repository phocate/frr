-- Create database if not exists
CREATE DATABASE IF NOT EXISTS frr;

-- Use the database
USE frr;

-- Create basic tables for initial setup
-- These will be managed by Flask-Migrate, but this creates the initial structure

-- Create a table for agencies
CREATE TABLE IF NOT EXISTS agency (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    abbreviation VARCHAR(20),
    description TEXT
);

-- Create a table for committees
CREATE TABLE IF NOT EXISTS committee (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- Create a junction table for agency-committee relationships
CREATE TABLE IF NOT EXISTS agency_committee (
    agency_id INT,
    committee_id INT,
    PRIMARY KEY (agency_id, committee_id),
    FOREIGN KEY (agency_id) REFERENCES agency(id),
    FOREIGN KEY (committee_id) REFERENCES committee(id)
);

-- Create a table for regulations
CREATE TABLE IF NOT EXISTS regulation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    rin VARCHAR(20) UNIQUE,
    agency_id INT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (agency_id) REFERENCES agency(id)
);

-- Create a table for rule stages
CREATE TABLE IF NOT EXISTS rule_stage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    regulation_id INT,
    stage_type VARCHAR(20) NOT NULL,
    publication_date DATE,
    federal_register_id VARCHAR(100),
    comment_end_date DATE,
    FOREIGN KEY (regulation_id) REFERENCES regulation(id)
);

-- Create a table for documents
CREATE TABLE IF NOT EXISTS document (
    id INT AUTO_INCREMENT PRIMARY KEY,
    regulation_id INT,
    title VARCHAR(255) NOT NULL,
    document_type VARCHAR(100),
    url VARCHAR(255),
    publication_date DATE,
    source VARCHAR(50),
    FOREIGN KEY (regulation_id) REFERENCES regulation(id)
);

-- Grant privileges to application user
GRANT ALL PRIVILEGES ON frr.* TO 'frr_user'@'%';
FLUSH PRIVILEGES;

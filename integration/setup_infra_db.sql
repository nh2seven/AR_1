-- Setup script for Infrastructure-Microservice database
-- Use this script to initialize the database for the Infrastructure-Microservice services

CREATE DATABASE IF NOT EXISTS INFRA_CC;
USE INFRA_CC;

-- Drop existing tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS server_stats;
DROP TABLE IF EXISTS lab_access_log;
DROP TABLE IF EXISTS lab_server;
DROP TABLE IF EXISTS labs;
DROP TABLE IF EXISTS servers;

-- Table 1: Servers
CREATE TABLE IF NOT EXISTS servers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(50) NOT NULL,
    cpu_usage FLOAT DEFAULT 0,
    memory_usage FLOAT DEFAULT 0,
    disk_usage FLOAT DEFAULT 0,
    max_cpu FLOAT DEFAULT 100,
    max_memory FLOAT DEFAULT 100,
    max_disk FLOAT DEFAULT 100,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table 2: Labs
CREATE TABLE IF NOT EXISTS labs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    status ENUM('active', 'inactive', 'deleted') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estimated_users INT DEFAULT 10,
    estimated_cpu FLOAT DEFAULT 10,
    estimated_memory FLOAT DEFAULT 20,
    estimated_disk FLOAT DEFAULT 5,
    avg_users FLOAT DEFAULT NULL,
    avg_time FLOAT DEFAULT NULL,
    total_sessions INT DEFAULT 0,
    total_user_minutes INT DEFAULT 0
);

-- Table 3: Lab-Server Allocations
CREATE TABLE IF NOT EXISTS lab_server (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lab_id INT NOT NULL,
    server_id INT NOT NULL,
    cpu_allocated INT DEFAULT 0,
    memory_allocated INT DEFAULT 0,
    disk_allocated INT DEFAULT 0,
    FOREIGN KEY (lab_id) REFERENCES labs(id) ON DELETE CASCADE,
    FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE,
    UNIQUE KEY unique_lab_server (lab_id, server_id)
);

-- Table 4: Lab Access Log
CREATE TABLE IF NOT EXISTS lab_access_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lab_id INT,
    user_count INT,
    duration_minutes INT,
    accessed_at DATETIME DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (lab_id) REFERENCES labs(id)
);

-- Table 5: Server Stats
CREATE TABLE IF NOT EXISTS server_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server_id INT NOT NULL,
    cpu_usage FLOAT DEFAULT 0,
    memory_usage FLOAT DEFAULT 0,
    disk_usage FLOAT DEFAULT 0,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (server_id) REFERENCES servers(id) ON DELETE CASCADE
);

-- Table 6: Logs
CREATE TABLE IF NOT EXISTS logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample servers
INSERT INTO servers (ip_address, cpu_usage, memory_usage, disk_usage, max_cpu, max_memory, max_disk)
VALUES 
('192.168.0.101', 15.5, 48.2, 72.9, 100, 128, 500),
('192.168.0.102', 23.7, 55.1, 80.3, 100, 128, 500);

-- Insert sample labs
INSERT INTO labs (name, status, estimated_users, estimated_cpu, estimated_memory, estimated_disk)
VALUES 
('Linux Basics', 'active', 15, 2, 4, 10),
('Docker', 'active', 10, 4, 8, 20),
('Kubernetes', 'active', 8, 8, 16, 30),
('Networking', 'active', 12, 2, 4, 5),
('Filesystem', 'active', 15, 1, 2, 8);

-- Insert sample lab-server allocations
INSERT INTO lab_server (lab_id, server_id, cpu_allocated, memory_allocated, disk_allocated)
VALUES 
(1, 1, 30, 60, 150),
(2, 1, 40, 80, 200),
(3, 2, 64, 128, 240),
(4, 2, 24, 48, 60),
(5, 1, 15, 30, 120);

-- Insert sample lab access logs
INSERT INTO lab_access_log (lab_id, user_count, duration_minutes, accessed_at)
VALUES 
(1, 12, 45, NOW() - INTERVAL 1 DAY),
(1, 8, 30, NOW() - INTERVAL 2 DAY),
(2, 6, 60, NOW() - INTERVAL 1 DAY),
(3, 5, 90, NOW() - INTERVAL 3 DAY),
(4, 10, 45, NOW() - INTERVAL 2 DAY),
(5, 14, 30, NOW() - INTERVAL 1 DAY);

-- Insert server stats
INSERT INTO server_stats (server_id, cpu_usage, memory_usage, disk_usage, recorded_at)
VALUES
(1, 60, 70, 65, NOW() - INTERVAL 1 HOUR),
(1, 65, 75, 68, NOW() - INTERVAL 30 MINUTE),
(1, 70, 80, 70, NOW()),
(2, 40, 60, 50, NOW() - INTERVAL 1 HOUR),
(2, 45, 65, 55, NOW() - INTERVAL 30 MINUTE),
(2, 50, 70, 60, NOW());

-- Create a dedicated database user for the application
CREATE USER IF NOT EXISTS 'infrauser'@'localhost' IDENTIFIED BY 'infrapassword';
GRANT ALL PRIVILEGES ON INFRA_CC.* TO 'infrauser'@'localhost';
FLUSH PRIVILEGES;
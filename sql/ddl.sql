-- TCL Interview Assignment — TestDB / tblTicketDetails
-- Run as a user with CREATE privileges (e.g. root or admin).

CREATE DATABASE IF NOT EXISTS TestDB
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE TestDB;

-- Application table (matches assignment spec)
CREATE TABLE IF NOT EXISTS tblTicketDetails (
  ticket_id     INT NOT NULL AUTO_INCREMENT,
  title         VARCHAR(512) NOT NULL,
  description   TEXT NULL,
  status        TEXT NOT NULL,
  priority      ENUM('LOW', 'MEDIUM', 'HIGH') NOT NULL DEFAULT 'MEDIUM',
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  assigned_to   VARCHAR(255) NULL,
  PRIMARY KEY (ticket_id),
  INDEX idx_tblTicketDetails_status (status(64)),
  INDEX idx_tblTicketDetails_priority (priority),
  INDEX idx_tblTicketDetails_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Optional: seed row for manual smoke tests (comment out if not needed)
-- INSERT INTO tblTicketDetails (title, description, status, priority, assigned_to)
-- VALUES ('Sample', 'Demo ticket', 'open', 'LOW', 'unassigned');

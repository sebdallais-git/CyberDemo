-- ============================================================
-- Snowflake Ransomware Scenario Data
-- ============================================================
-- LockBit 4.0 attack on pharma SCADA infrastructure.
-- Hosts aligned with the IT/OT Infrastructure page.
-- Loaded via TRUNCATE + INSERT at scenario start.
-- ============================================================

USE DATABASE CYBER_SECURITY;
USE SCHEMA SIEM;

-- ── ANOMALY_SCORES: 4 compromised hosts ──────────────────────
-- Use INSERT ... SELECT because PARSE_JSON() is not allowed in VALUES clause

INSERT INTO ANOMALY_SCORES (score_id, entity_type, entity_name, entity_ip, current_score, baseline_score, anomaly_delta, anomaly_label, contributing_factors, model_version, computed_at)
SELECT 'AS-RW-001', 'HOST', 'SCADA-HIST-01', '10.20.1.10', 9.87, 1.1, 8.77, 'CRITICAL_ANOMALY',
       PARSE_JSON('{
           "encryption_activity": "EXTREME",
           "ransomware_family": "LockBit 4.0",
           "data_encrypted": "batch records + temperature logs",
           "ransom_note_dropped": true,
           "outbound_to_rogue_ip": true,
           "spread_from": "gateway server"
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

INSERT INTO ANOMALY_SCORES (score_id, entity_type, entity_name, entity_ip, current_score, baseline_score, anomaly_delta, anomaly_label, contributing_factors, model_version, computed_at)
SELECT 'AS-RW-002', 'HOST', 'XR4000-EDGE-01', '10.10.1.10', 8.50, 0.9, 7.60, 'CRITICAL_ANOMALY',
       PARSE_JSON('{
           "initial_access": "phished employee credential",
           "credential_theft": "admin password harvested",
           "attacker_toolkit_detected": true,
           "outbound_to_rogue_ip": true,
           "role": "entry point — gateway into OT network"
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

INSERT INTO ANOMALY_SCORES (score_id, entity_type, entity_name, entity_ip, current_score, baseline_score, anomaly_delta, anomaly_label, contributing_factors, model_version, computed_at)
SELECT 'AS-RW-003', 'HOST', 'SCADA-HIST-02', '10.20.1.20', 7.90, 1.0, 6.90, 'HIGH_ANOMALY',
       PARSE_JSON('{
           "encryption_activity": "HIGH",
           "spread_via_replication": true,
           "encrypted_data_from": "SCADA-HIST-01 via HA sync",
           "archive_corrupted": "6 months of batch records"
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

INSERT INTO ANOMALY_SCORES (score_id, entity_type, entity_name, entity_ip, current_score, baseline_score, anomaly_delta, anomaly_label, contributing_factors, model_version, computed_at)
SELECT 'AS-RW-004', 'HOST', 'POWERSCALE-01', '10.35.1.10', 6.80, 0.8, 6.00, 'HIGH_ANOMALY',
       PARSE_JSON('{
           "file_share_scanning": "archive share enumeration",
           "suspicious_read_pattern": "sequential scan of pharma archive",
           "backup_deletion_attempted": true,
           "spread_from": "gateway server"
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

-- ── ENDPOINT_EVENTS: 10 detections ──────────────────────────

INSERT INTO ENDPOINT_EVENTS (event_id, hostname, event_type, severity, detection_name, risk_score, process_name, file_path, event_time)
VALUES
    ('EVT-RW-001', 'SCADA-HIST-01', 'RANSOMWARE', 'CRITICAL', 'Ransomware.Encrypt.BatchRecords', 9.95, 'lockbit.exe', 'D:\\PIServer\\Data\\piarch\\', CURRENT_TIMESTAMP()),
    ('EVT-RW-002', 'SCADA-HIST-01', 'RANSOMWARE', 'CRITICAL', 'Ransomware.RansomNote.Dropped', 9.90, 'lockbit.exe', 'C:\\README_RESTORE.txt', CURRENT_TIMESTAMP()),
    ('EVT-RW-003', 'SCADA-HIST-01', 'OUTBOUND', 'CRITICAL', 'Suspicious.Outbound.RogueIP', 9.80, 'rundll32.exe', NULL, CURRENT_TIMESTAMP()),
    ('EVT-RW-004', 'XR4000-EDGE-01', 'CREDENTIAL_THEFT', 'CRITICAL', 'Admin.Credential.Harvested', 9.70, 'credential_tool.exe', NULL, CURRENT_TIMESTAMP()),
    ('EVT-RW-005', 'XR4000-EDGE-01', 'EXPLOIT', 'CRITICAL', 'Remote.Access.Exploited', 9.60, 'ScreenConnect.exe', NULL, CURRENT_TIMESTAMP()),
    ('EVT-RW-006', 'XR4000-EDGE-01', 'OUTBOUND', 'HIGH', 'Suspicious.Outbound.RogueIP', 8.50, 'svchost.exe', NULL, CURRENT_TIMESTAMP()),
    ('EVT-RW-007', 'SCADA-HIST-02', 'RANSOMWARE', 'HIGH', 'Ransomware.Spread.ViaReplication', 8.30, 'lockbit.exe', 'D:\\PIServer\\Data\\', CURRENT_TIMESTAMP()),
    ('EVT-RW-008', 'SCADA-HIST-02', 'FILE_SYSTEM', 'HIGH', 'Backup.Deletion.Attempted', 8.10, 'vssadmin.exe', NULL, CURRENT_TIMESTAMP()),
    ('EVT-RW-009', 'POWERSCALE-01', 'LATERAL_MOVEMENT', 'HIGH', 'FileShare.Scanning.Archive', 7.50, 'net.exe', '\\\\POWERSCALE-01\\pharma-archive\\', CURRENT_TIMESTAMP()),
    ('EVT-RW-010', 'POWERSCALE-01', 'FILE_SYSTEM', 'HIGH', 'Backup.Deletion.Attempted', 7.20, 'wmic.exe', NULL, CURRENT_TIMESTAMP());

-- ── NETWORK_EVENTS: 20 flows ─────────────────────────────────

INSERT INTO NETWORK_EVENTS (event_id, source_host, source_ip, dest_ip, dest_port, protocol, bytes_sent, bytes_received, geo_country, event_time)
VALUES
    -- XR4000-EDGE-01: outbound to rogue IPs
    ('NET-RW-001', 'XR4000-EDGE-01', '10.10.1.10', '185.220.101.35', 8443, 'TCP', 128000, 45000, 'XX', CURRENT_TIMESTAMP()),
    ('NET-RW-002', 'XR4000-EDGE-01', '10.10.1.10', '185.220.101.35', 8443, 'TCP', 95000, 32000, 'XX', CURRENT_TIMESTAMP()),
    ('NET-RW-003', 'XR4000-EDGE-01', '10.10.1.10', '185.220.101.36', 443, 'TCP', 64000, 28000, 'XX', CURRENT_TIMESTAMP()),
    -- XR4000-EDGE-01: lateral movement to SCADA-HIST-01
    ('NET-RW-004', 'XR4000-EDGE-01', '10.10.1.10', '10.20.1.10', 445, 'SMB', 4500000, 1024, 'CH', CURRENT_TIMESTAMP()),
    ('NET-RW-005', 'XR4000-EDGE-01', '10.10.1.10', '10.20.1.10', 445, 'SMB', 3200000, 512, 'CH', CURRENT_TIMESTAMP()),
    -- XR4000-EDGE-01: lateral movement to POWERSCALE-01
    ('NET-RW-006', 'XR4000-EDGE-01', '10.10.1.10', '10.35.1.10', 445, 'SMB', 820000, 256, 'CH', CURRENT_TIMESTAMP()),
    ('NET-RW-007', 'XR4000-EDGE-01', '10.10.1.10', '10.35.1.10', 445, 'SMB', 640000, 128, 'CH', CURRENT_TIMESTAMP()),
    -- SCADA-HIST-01: outbound to rogue IPs
    ('NET-RW-008', 'SCADA-HIST-01', '10.20.1.10', '185.220.101.34', 443, 'TCP', 312000, 18000, 'XX', CURRENT_TIMESTAMP()),
    ('NET-RW-009', 'SCADA-HIST-01', '10.20.1.10', '185.220.101.34', 443, 'TCP', 245000, 15000, 'XX', CURRENT_TIMESTAMP()),
    ('NET-RW-010', 'SCADA-HIST-01', '10.20.1.10', '185.220.101.34', 443, 'TCP', 180000, 12000, 'XX', CURRENT_TIMESTAMP()),
    -- SCADA-HIST-01: HA replication spreading encrypted data
    ('NET-RW-011', 'SCADA-HIST-01', '10.20.1.10', '10.20.1.20', 5457, 'TCP', 890000000, 4096, 'CH', CURRENT_TIMESTAMP()),
    ('NET-RW-012', 'SCADA-HIST-01', '10.20.1.10', '10.20.1.20', 5457, 'TCP', 650000000, 2048, 'CH', CURRENT_TIMESTAMP()),
    ('NET-RW-013', 'SCADA-HIST-01', '10.20.1.10', '10.20.1.20', 5457, 'TCP', 420000000, 1024, 'CH', CURRENT_TIMESTAMP()),
    -- SCADA-HIST-01: file share spreading to POWERSCALE-01
    ('NET-RW-014', 'SCADA-HIST-01', '10.20.1.10', '10.35.1.10', 445, 'SMB', 1200000, 512, 'CH', CURRENT_TIMESTAMP()),
    ('NET-RW-015', 'SCADA-HIST-01', '10.20.1.10', '10.35.1.10', 445, 'SMB', 980000, 256, 'CH', CURRENT_TIMESTAMP()),
    -- SCADA-HIST-02: encrypted data via HA replication
    ('NET-RW-016', 'SCADA-HIST-02', '10.20.1.20', '10.20.1.10', 5457, 'TCP', 4096, 890000000, 'CH', CURRENT_TIMESTAMP()),
    -- POWERSCALE-01: file share probing
    ('NET-RW-017', 'POWERSCALE-01', '10.35.1.10', '10.20.1.10', 445, 'SMB', 64000, 128000, 'CH', CURRENT_TIMESTAMP()),
    ('NET-RW-018', 'POWERSCALE-01', '10.35.1.10', '10.20.1.20', 445, 'SMB', 48000, 96000, 'CH', CURRENT_TIMESTAMP()),
    -- Additional outbound to rogue IPs
    ('NET-RW-019', 'SCADA-HIST-01', '10.20.1.10', '185.220.101.37', 8080, 'TCP', 92000, 8000, 'XX', CURRENT_TIMESTAMP()),
    ('NET-RW-020', 'XR4000-EDGE-01', '10.10.1.10', '185.220.101.38', 443, 'TCP', 78000, 6000, 'XX', CURRENT_TIMESTAMP());

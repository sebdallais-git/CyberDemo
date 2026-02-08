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
           "lockbit4_signature": true,
           "pi_database_encrypted": "batch records + temp logs",
           "ransom_note_dropped": "README_RESTORE.txt",
           "c2_callback": "185.220.101.34:443 (RU)",
           "lateral_source": "XR4000-EDGE-01"
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

INSERT INTO ANOMALY_SCORES (score_id, entity_type, entity_name, entity_ip, current_score, baseline_score, anomaly_delta, anomaly_label, contributing_factors, model_version, computed_at)
SELECT 'AS-RW-002', 'HOST', 'XR4000-EDGE-01', '10.10.1.10', 8.50, 0.9, 7.60, 'CRITICAL_ANOMALY',
       PARSE_JSON('{
           "initial_access": "phished VPN credential",
           "credential_dumping": "LSASS memory dump",
           "cobalt_strike_beacon": true,
           "c2_callback": "185.220.101.35:8443 (RU)",
           "privilege_escalation": "CVE-2024-1709 (ScreenConnect)"
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

INSERT INTO ANOMALY_SCORES (score_id, entity_type, entity_name, entity_ip, current_score, baseline_score, anomaly_delta, anomaly_label, contributing_factors, model_version, computed_at)
SELECT 'AS-RW-003', 'HOST', 'SCADA-HIST-02', '10.20.1.20', 7.90, 1.0, 6.90, 'HIGH_ANOMALY',
       PARSE_JSON('{
           "encryption_activity": "HIGH",
           "ha_replication_spread": true,
           "encrypted_data_from": "SCADA-HIST-01 via HA sync",
           "pi_archive_corrupted": "6 months of batch records"
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

INSERT INTO ANOMALY_SCORES (score_id, entity_type, entity_name, entity_ip, current_score, baseline_score, anomaly_delta, anomaly_label, contributing_factors, model_version, computed_at)
SELECT 'AS-RW-004', 'HOST', 'POWERSCALE-01', '10.35.1.10', 6.80, 0.8, 6.00, 'HIGH_ANOMALY',
       PARSE_JSON('{
           "smb_probing": "archive share enumeration",
           "suspicious_read_pattern": "sequential scan of /pharma-archive/",
           "volume_shadow_deletion": "attempted",
           "lateral_source": "XR4000-EDGE-01"
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

-- ── ENDPOINT_EVENTS: 10 detections ──────────────────────────

INSERT INTO ENDPOINT_EVENTS (event_id, hostname, event_type, severity, detection_name, risk_score, process_name, file_path, event_time)
VALUES
    ('EVT-RW-001', 'SCADA-HIST-01', 'RANSOMWARE', 'CRITICAL', 'LockBit4.Encrypt.PIDatabase', 9.95, 'lockbit.exe', 'D:\\PIServer\\Data\\piarch\\', CURRENT_TIMESTAMP()),
    ('EVT-RW-002', 'SCADA-HIST-01', 'RANSOMWARE', 'CRITICAL', 'LockBit4.RansomNote.Drop', 9.90, 'lockbit.exe', 'C:\\README_RESTORE.txt', CURRENT_TIMESTAMP()),
    ('EVT-RW-003', 'SCADA-HIST-01', 'C2_CALLBACK', 'CRITICAL', 'CobaltStrike.Beacon.HTTPS', 9.80, 'rundll32.exe', NULL, CURRENT_TIMESTAMP()),
    ('EVT-RW-004', 'XR4000-EDGE-01', 'CREDENTIAL_THEFT', 'CRITICAL', 'Mimikatz.LSASS.Dump', 9.70, 'mimikatz.exe', NULL, CURRENT_TIMESTAMP()),
    ('EVT-RW-005', 'XR4000-EDGE-01', 'EXPLOIT', 'CRITICAL', 'CVE-2024-1709.ScreenConnect', 9.60, 'ScreenConnect.exe', NULL, CURRENT_TIMESTAMP()),
    ('EVT-RW-006', 'XR4000-EDGE-01', 'C2_CALLBACK', 'HIGH', 'CobaltStrike.Beacon.DNS', 8.50, 'svchost.exe', NULL, CURRENT_TIMESTAMP()),
    ('EVT-RW-007', 'SCADA-HIST-02', 'RANSOMWARE', 'HIGH', 'LockBit4.Encrypt.HASpread', 8.30, 'lockbit.exe', 'D:\\PIServer\\Data\\', CURRENT_TIMESTAMP()),
    ('EVT-RW-008', 'SCADA-HIST-02', 'FILE_SYSTEM', 'HIGH', 'VSS.ShadowCopy.Delete', 8.10, 'vssadmin.exe', NULL, CURRENT_TIMESTAMP()),
    ('EVT-RW-009', 'POWERSCALE-01', 'LATERAL_MOVEMENT', 'HIGH', 'SMB.ShareEnum.Archive', 7.50, 'net.exe', '\\\\POWERSCALE-01\\pharma-archive\\', CURRENT_TIMESTAMP()),
    ('EVT-RW-010', 'POWERSCALE-01', 'FILE_SYSTEM', 'HIGH', 'VSS.ShadowCopy.Delete.Attempt', 7.20, 'wmic.exe', NULL, CURRENT_TIMESTAMP());

-- ── NETWORK_EVENTS: 20 flows ─────────────────────────────────

INSERT INTO NETWORK_EVENTS (event_id, source_host, source_ip, dest_ip, dest_port, protocol, bytes_sent, bytes_received, geo_country, event_time)
VALUES
    -- XR4000-EDGE-01: C2 callbacks to Russia
    ('NET-RW-001', 'XR4000-EDGE-01', '10.10.1.10', '185.220.101.35', 8443, 'TCP', 128000, 45000, 'RU', CURRENT_TIMESTAMP()),
    ('NET-RW-002', 'XR4000-EDGE-01', '10.10.1.10', '185.220.101.35', 8443, 'TCP', 95000, 32000, 'RU', CURRENT_TIMESTAMP()),
    ('NET-RW-003', 'XR4000-EDGE-01', '10.10.1.10', '185.220.101.36', 443, 'TCP', 64000, 28000, 'RU', CURRENT_TIMESTAMP()),
    -- XR4000-EDGE-01: lateral to SCADA-HIST-01
    ('NET-RW-004', 'XR4000-EDGE-01', '10.10.1.10', '10.20.1.10', 445, 'SMB', 4500000, 1024, 'CH', CURRENT_TIMESTAMP()),
    ('NET-RW-005', 'XR4000-EDGE-01', '10.10.1.10', '10.20.1.10', 445, 'SMB', 3200000, 512, 'CH', CURRENT_TIMESTAMP()),
    -- XR4000-EDGE-01: lateral to POWERSCALE-01
    ('NET-RW-006', 'XR4000-EDGE-01', '10.10.1.10', '10.35.1.10', 445, 'SMB', 820000, 256, 'CH', CURRENT_TIMESTAMP()),
    ('NET-RW-007', 'XR4000-EDGE-01', '10.10.1.10', '10.35.1.10', 445, 'SMB', 640000, 128, 'CH', CURRENT_TIMESTAMP()),
    -- SCADA-HIST-01: C2 callbacks
    ('NET-RW-008', 'SCADA-HIST-01', '10.20.1.10', '185.220.101.34', 443, 'TCP', 312000, 18000, 'RU', CURRENT_TIMESTAMP()),
    ('NET-RW-009', 'SCADA-HIST-01', '10.20.1.10', '185.220.101.34', 443, 'TCP', 245000, 15000, 'RU', CURRENT_TIMESTAMP()),
    ('NET-RW-010', 'SCADA-HIST-01', '10.20.1.10', '185.220.101.34', 443, 'TCP', 180000, 12000, 'RU', CURRENT_TIMESTAMP()),
    -- SCADA-HIST-01: HA replication spreading encrypted data
    ('NET-RW-011', 'SCADA-HIST-01', '10.20.1.10', '10.20.1.20', 5457, 'TCP', 890000000, 4096, 'CH', CURRENT_TIMESTAMP()),
    ('NET-RW-012', 'SCADA-HIST-01', '10.20.1.10', '10.20.1.20', 5457, 'TCP', 650000000, 2048, 'CH', CURRENT_TIMESTAMP()),
    ('NET-RW-013', 'SCADA-HIST-01', '10.20.1.10', '10.20.1.20', 5457, 'TCP', 420000000, 1024, 'CH', CURRENT_TIMESTAMP()),
    -- SCADA-HIST-01: SMB to POWERSCALE-01
    ('NET-RW-014', 'SCADA-HIST-01', '10.20.1.10', '10.35.1.10', 445, 'SMB', 1200000, 512, 'CH', CURRENT_TIMESTAMP()),
    ('NET-RW-015', 'SCADA-HIST-01', '10.20.1.10', '10.35.1.10', 445, 'SMB', 980000, 256, 'CH', CURRENT_TIMESTAMP()),
    -- SCADA-HIST-02: encrypted HA traffic (receiving)
    ('NET-RW-016', 'SCADA-HIST-02', '10.20.1.20', '10.20.1.10', 5457, 'TCP', 4096, 890000000, 'CH', CURRENT_TIMESTAMP()),
    -- POWERSCALE-01: SMB probing
    ('NET-RW-017', 'POWERSCALE-01', '10.35.1.10', '10.20.1.10', 445, 'SMB', 64000, 128000, 'CH', CURRENT_TIMESTAMP()),
    ('NET-RW-018', 'POWERSCALE-01', '10.35.1.10', '10.20.1.20', 445, 'SMB', 48000, 96000, 'CH', CURRENT_TIMESTAMP()),
    -- Additional C2 beacon traffic
    ('NET-RW-019', 'SCADA-HIST-01', '10.20.1.10', '185.220.101.37', 8080, 'TCP', 92000, 8000, 'RU', CURRENT_TIMESTAMP()),
    ('NET-RW-020', 'XR4000-EDGE-01', '10.10.1.10', '185.220.101.38', 443, 'TCP', 78000, 6000, 'RU', CURRENT_TIMESTAMP());

-- ============================================================
-- Snowflake Data Exfiltration Scenario Data
-- ============================================================
-- Insider threat / APT slow exfiltration of GxP data via DNS
-- tunneling. LIMS, ERP, and clinical data warehouse targeted.
-- Loaded via TRUNCATE + INSERT at scenario start.
-- ============================================================

USE DATABASE CYBER_SECURITY;
USE SCHEMA SIEM;

-- ── ANOMALY_SCORES: 4 compromised hosts ──────────────────────
-- Use INSERT ... SELECT because PARSE_JSON() is not allowed in VALUES clause

INSERT INTO ANOMALY_SCORES (score_id, entity_type, entity_name, entity_ip, current_score, baseline_score, anomaly_delta, anomaly_label, contributing_factors, model_version, computed_at)
SELECT 'AS-DE-001', 'HOST', 'LIMS-DB-01', '10.50.2.10', 9.20, 1.0, 8.20, 'CRITICAL_ANOMALY',
       PARSE_JSON('{
           "bulk_data_access": "47000 rows/min (normal: 200/min)",
           "gxp_data_accessed": "validation records + batch genealogy",
           "compromised_account": true,
           "off_hours_activity": "02:00-05:00 CET — no legitimate user",
           "data_staging_detected": true
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

INSERT INTO ANOMALY_SCORES (score_id, entity_type, entity_name, entity_ip, current_score, baseline_score, anomaly_delta, anomaly_label, contributing_factors, model_version, computed_at)
SELECT 'AS-DE-002', 'HOST', 'DNS-PROXY-01', '10.50.3.10', 8.80, 0.7, 8.10, 'CRITICAL_ANOMALY',
       PARSE_JSON('{
           "covert_data_channel": true,
           "abnormal_traffic_pattern": "6x normal volume",
           "total_exfiltrated_est": "4.2 GB over 72 hours",
           "query_rate": "1200 queries/min (normal: 50)",
           "role": "data exfiltration conduit"
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

INSERT INTO ANOMALY_SCORES (score_id, entity_type, entity_name, entity_ip, current_score, baseline_score, anomaly_delta, anomaly_label, contributing_factors, model_version, computed_at)
SELECT 'AS-DE-003', 'HOST', 'ERP-CHEM-01', '10.50.2.20', 7.60, 0.9, 6.70, 'HIGH_ANOMALY',
       PARSE_JSON('{
           "synthesis_routes_accessed": "12 proprietary formulas",
           "bulk_export_pattern": true,
           "compromised_account_reused": true,
           "ip_theft_confirmed": "trade secret material exported"
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

INSERT INTO ANOMALY_SCORES (score_id, entity_type, entity_name, entity_ip, current_score, baseline_score, anomaly_delta, anomaly_label, contributing_factors, model_version, computed_at)
SELECT 'AS-DE-004', 'HOST', 'CLINICAL-DW-01', '10.50.2.30', 7.10, 1.2, 5.90, 'HIGH_ANOMALY',
       PARSE_JSON('{
           "patient_trial_data_accessed": "Phase III BPX-7721 cohort",
           "pii_exposure": "12000 patient records queried",
           "data_correlated": "demographics + outcomes + adverse events",
           "exported": true
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

-- ── ENDPOINT_EVENTS: 10 detections ──────────────────────────

INSERT INTO ENDPOINT_EVENTS (event_id, hostname, event_type, severity, detection_name, risk_score, process_name, file_path, event_time)
VALUES
    ('EVT-DE-001', 'LIMS-DB-01', 'DATA_EXFIL', 'CRITICAL', 'BulkAccess.GxPRecords', 9.50, 'sqlservr.exe', NULL, CURRENT_TIMESTAMP()),
    ('EVT-DE-002', 'LIMS-DB-01', 'CREDENTIAL_ABUSE', 'CRITICAL', 'Account.OffHoursAccess', 9.30, 'svc_lims_readonly', NULL, CURRENT_TIMESTAMP()),
    ('EVT-DE-003', 'LIMS-DB-01', 'FILE_STAGING', 'HIGH', 'Data.StagedForExport', 8.80, 'tar', '/tmp/.cache/lims_export/', CURRENT_TIMESTAMP()),
    ('EVT-DE-004', 'DNS-PROXY-01', 'COVERT_CHANNEL', 'CRITICAL', 'CovertChannel.DataExfil', 9.40, 'iodine', NULL, CURRENT_TIMESTAMP()),
    ('EVT-DE-005', 'DNS-PROXY-01', 'COVERT_CHANNEL', 'CRITICAL', 'AbnormalTraffic.HighVolume', 9.20, 'dns-tunnel-client', NULL, CURRENT_TIMESTAMP()),
    ('EVT-DE-006', 'DNS-PROXY-01', 'OUTBOUND', 'HIGH', 'Suspicious.Outbound.Channel', 8.60, 'resolved', NULL, CURRENT_TIMESTAMP()),
    ('EVT-DE-007', 'ERP-CHEM-01', 'DATA_EXFIL', 'HIGH', 'BulkExport.SynthesisRoutes', 8.40, 'sap_export.sh', '/opt/erp/export/', CURRENT_TIMESTAMP()),
    ('EVT-DE-008', 'ERP-CHEM-01', 'FILE_STAGING', 'HIGH', 'IPTheft.FormulasExported', 8.10, 'tar', '/opt/erp/export/chem_routes.tar.gz', CURRENT_TIMESTAMP()),
    ('EVT-DE-009', 'CLINICAL-DW-01', 'DATA_EXFIL', 'HIGH', 'BulkQuery.PatientTrialData', 7.80, 'psql', NULL, CURRENT_TIMESTAMP()),
    ('EVT-DE-010', 'CLINICAL-DW-01', 'PII_ACCESS', 'HIGH', 'PatientPII.BulkAccess', 7.50, 'psql', NULL, CURRENT_TIMESTAMP());

-- ── NETWORK_EVENTS: 20 flows ─────────────────────────────────

INSERT INTO NETWORK_EVENTS (event_id, source_host, source_ip, dest_ip, dest_port, protocol, bytes_sent, bytes_received, geo_country, event_time)
VALUES
    -- DNS-PROXY-01: DNS tunneling to exfil domain (port 53)
    ('NET-DE-001', 'DNS-PROXY-01', '10.50.3.10', '198.51.100.53', 53, 'UDP', 420000, 8000, 'US', CURRENT_TIMESTAMP()),
    ('NET-DE-002', 'DNS-PROXY-01', '10.50.3.10', '198.51.100.53', 53, 'UDP', 385000, 7500, 'US', CURRENT_TIMESTAMP()),
    ('NET-DE-003', 'DNS-PROXY-01', '10.50.3.10', '198.51.100.53', 53, 'UDP', 410000, 8200, 'US', CURRENT_TIMESTAMP()),
    ('NET-DE-004', 'DNS-PROXY-01', '10.50.3.10', '198.51.100.54', 53, 'UDP', 350000, 6800, 'US', CURRENT_TIMESTAMP()),
    ('NET-DE-005', 'DNS-PROXY-01', '10.50.3.10', '198.51.100.54', 53, 'UDP', 395000, 7200, 'US', CURRENT_TIMESTAMP()),
    -- DNS-PROXY-01: HTTPS exfil backup channel
    ('NET-DE-006', 'DNS-PROXY-01', '10.50.3.10', '203.0.113.99', 443, 'TCP', 890000, 12000, 'SG', CURRENT_TIMESTAMP()),
    ('NET-DE-007', 'DNS-PROXY-01', '10.50.3.10', '203.0.113.99', 443, 'TCP', 720000, 9500, 'SG', CURRENT_TIMESTAMP()),
    -- LIMS-DB-01: data transfer to DNS-PROXY-01 (internal staging)
    ('NET-DE-008', 'LIMS-DB-01', '10.50.2.10', '10.50.3.10', 8443, 'TCP', 1200000000, 4096, 'CH', CURRENT_TIMESTAMP()),
    ('NET-DE-009', 'LIMS-DB-01', '10.50.2.10', '10.50.3.10', 8443, 'TCP', 980000000, 2048, 'CH', CURRENT_TIMESTAMP()),
    ('NET-DE-010', 'LIMS-DB-01', '10.50.2.10', '10.50.3.10', 8443, 'TCP', 850000000, 1024, 'CH', CURRENT_TIMESTAMP()),
    -- ERP-CHEM-01: data transfer to DNS-PROXY-01
    ('NET-DE-011', 'ERP-CHEM-01', '10.50.2.20', '10.50.3.10', 8443, 'TCP', 620000000, 2048, 'CH', CURRENT_TIMESTAMP()),
    ('NET-DE-012', 'ERP-CHEM-01', '10.50.2.20', '10.50.3.10', 8443, 'TCP', 480000000, 1024, 'CH', CURRENT_TIMESTAMP()),
    -- CLINICAL-DW-01: data transfer to DNS-PROXY-01
    ('NET-DE-013', 'CLINICAL-DW-01', '10.50.2.30', '10.50.3.10', 8443, 'TCP', 340000000, 2048, 'CH', CURRENT_TIMESTAMP()),
    ('NET-DE-014', 'CLINICAL-DW-01', '10.50.2.30', '10.50.3.10', 8443, 'TCP', 280000000, 1024, 'CH', CURRENT_TIMESTAMP()),
    -- Additional DNS tunneling traffic
    ('NET-DE-015', 'DNS-PROXY-01', '10.50.3.10', '198.51.100.53', 53, 'UDP', 440000, 8500, 'US', CURRENT_TIMESTAMP()),
    ('NET-DE-016', 'DNS-PROXY-01', '10.50.3.10', '198.51.100.53', 53, 'UDP', 380000, 7100, 'US', CURRENT_TIMESTAMP()),
    ('NET-DE-017', 'DNS-PROXY-01', '10.50.3.10', '198.51.100.55', 53, 'UDP', 290000, 5500, 'US', CURRENT_TIMESTAMP()),
    ('NET-DE-018', 'DNS-PROXY-01', '10.50.3.10', '198.51.100.55', 53, 'UDP', 310000, 6000, 'US', CURRENT_TIMESTAMP()),
    -- LIMS-DB-01: suspicious outbound (rare for DB server)
    ('NET-DE-019', 'LIMS-DB-01', '10.50.2.10', '203.0.113.100', 443, 'TCP', 45000, 3200, 'SG', CURRENT_TIMESTAMP()),
    ('NET-DE-020', 'LIMS-DB-01', '10.50.2.10', '203.0.113.100', 443, 'TCP', 38000, 2800, 'SG', CURRENT_TIMESTAMP());

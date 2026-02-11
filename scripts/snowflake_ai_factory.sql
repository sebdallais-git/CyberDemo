-- ============================================================
-- Snowflake AI Factory Scenario Data
-- ============================================================
-- Nation-state intrusion on AI drug discovery
-- pipeline. GPU cluster, MLOps platform, and PowerScale data
-- lake compromised. Loaded via TRUNCATE + INSERT at scenario start.
-- ============================================================

USE DATABASE CYBER_SECURITY;
USE SCHEMA SIEM;

-- ── ANOMALY_SCORES: 4 AI Factory hosts ──────────────────────
-- Use INSERT ... SELECT because PARSE_JSON() is not allowed in VALUES clause

INSERT INTO ANOMALY_SCORES (score_id, entity_type, entity_name, entity_ip, current_score, baseline_score, anomaly_delta, anomaly_label, contributing_factors, model_version, computed_at)
SELECT 'AS-AI-001', 'HOST', 'GPU-TRAIN-01', '10.30.1.10', 9.92, 1.2, 8.72, 'CRITICAL_ANOMALY',
       PARSE_JSON('{
           "encryption_activity": "EXTREME",
           "wiper_payload_detected": true,
           "training_data_destroyed": "2.1TB in 47s",
           "outbound_to_rogue_ip": true,
           "spread_from": "ML platform",
           "gpu_utilization_anomaly": "0% (normally 85%)"
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

INSERT INTO ANOMALY_SCORES (score_id, entity_type, entity_name, entity_ip, current_score, baseline_score, anomaly_delta, anomaly_label, contributing_factors, model_version, computed_at)
SELECT 'AS-AI-002', 'HOST', 'MLOPS-01', '10.30.3.10', 8.70, 1.5, 7.20, 'CRITICAL_ANOMALY',
       PARSE_JSON('{
           "stolen_credentials": true,
           "bulk_data_export": "14000 API calls in 3 min",
           "experiments_encrypted": 2847,
           "credential_theft": "service account compromised",
           "anomalous_pattern": "bulk export never seen before"
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

INSERT INTO ANOMALY_SCORES (score_id, entity_type, entity_name, entity_ip, current_score, baseline_score, anomaly_delta, anomaly_label, contributing_factors, model_version, computed_at)
SELECT 'AS-AI-003', 'HOST', 'AI-DATA-01', '10.30.2.10', 7.80, 1.1, 6.70, 'HIGH_ANOMALY',
       PARSE_JSON('{
           "lateral_movement_indicator": true,
           "smb_encryption_spray": "PowerScale /ai-data/training/*",
           "delta_lake_tables_at_risk": true,
           "unexpected_nfs_source": "GPU-TRAIN-01"
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

INSERT INTO ANOMALY_SCORES (score_id, entity_type, entity_name, entity_ip, current_score, baseline_score, anomaly_delta, anomaly_label, contributing_factors, model_version, computed_at)
SELECT 'AS-AI-004', 'HOST', 'GPU-INF-01', '10.30.1.20', 6.10, 1.3, 4.80, 'HIGH_ANOMALY',
       PARSE_JSON('{
           "lateral_movement_indicator": true,
           "model_serving_disrupted": true,
           "unexpected_smb_source": "GPU-TRAIN-01"
       }'),
       'sf-anomaly-v3.2', CURRENT_TIMESTAMP();

-- ── DATABRICKS_API_EVENTS: 15 rows — the "smoking gun" ──────
-- Normal baseline (2 calls), then a burst of 13 calls in ~3 min
-- from the stolen service principal svc-unity-rd-pipeline

INSERT INTO DATABRICKS_API_EVENTS (event_id, event_time, service_principal, api_endpoint, http_method, status_code, response_bytes, source_ip, catalog_name, tables_accessed, is_anomalous)
VALUES
    -- Baseline: normal automated calls (daily catalog sync)
    ('DBX-AI-001', DATEADD(MINUTE, -120, CURRENT_TIMESTAMP()), 'svc-unity-rd-pipeline', '/api/2.1/unity-catalog/tables', 'GET', 200, 4200, '10.30.3.10', 'rd_pharma', 12, FALSE),
    ('DBX-AI-002', DATEADD(MINUTE, -60, CURRENT_TIMESTAMP()), 'svc-unity-rd-pipeline', '/api/2.1/unity-catalog/schemas', 'GET', 200, 1800, '10.30.3.10', 'rd_pharma', 0, FALSE),
    -- Attack burst begins: bulk catalog listing from stolen credential
    ('DBX-AI-003', DATEADD(SECOND, -180, CURRENT_TIMESTAMP()), 'svc-unity-rd-pipeline', '/api/2.1/unity-catalog/tables?catalog=rd_pharma', 'GET', 200, 2800000, '91.234.99.44', 'rd_pharma', 14247, TRUE),
    ('DBX-AI-004', DATEADD(SECOND, -165, CURRENT_TIMESTAMP()), 'svc-unity-rd-pipeline', '/api/2.1/unity-catalog/tables?catalog=clinical_trials', 'GET', 200, 1450000, '91.234.99.44', 'clinical_trials', 8432, TRUE),
    ('DBX-AI-005', DATEADD(SECOND, -150, CURRENT_TIMESTAMP()), 'svc-unity-rd-pipeline', '/api/2.1/unity-catalog/volumes/list', 'GET', 200, 890000, '91.234.99.44', 'rd_pharma', 0, TRUE),
    ('DBX-AI-006', DATEADD(SECOND, -135, CURRENT_TIMESTAMP()), 'svc-unity-rd-pipeline', '/api/2.0/mlflow/experiments/search', 'GET', 200, 3200000, '91.234.99.44', 'rd_pharma', 0, TRUE),
    ('DBX-AI-007', DATEADD(SECOND, -120, CURRENT_TIMESTAMP()), 'svc-unity-rd-pipeline', '/api/2.0/mlflow/runs/search', 'POST', 200, 18500000, '91.234.99.44', 'rd_pharma', 0, TRUE),
    ('DBX-AI-008', DATEADD(SECOND, -105, CURRENT_TIMESTAMP()), 'svc-unity-rd-pipeline', '/api/2.0/mlflow/artifacts/list?run_id=BPX7721-v142', 'GET', 200, 4700000, '91.234.99.44', 'rd_pharma', 0, TRUE),
    ('DBX-AI-009', DATEADD(SECOND, -90, CURRENT_TIMESTAMP()), 'svc-unity-rd-pipeline', '/api/2.1/unity-catalog/tables/rd_pharma.molecular.sims/export', 'POST', 200, 42000000, '91.234.99.44', 'rd_pharma', 1, TRUE),
    ('DBX-AI-010', DATEADD(SECOND, -75, CURRENT_TIMESTAMP()), 'svc-unity-rd-pipeline', '/api/2.1/unity-catalog/tables/rd_pharma.genomics.sequences/export', 'POST', 200, 38000000, '91.234.99.44', 'rd_pharma', 1, TRUE),
    ('DBX-AI-011', DATEADD(SECOND, -60, CURRENT_TIMESTAMP()), 'svc-unity-rd-pipeline', '/api/2.1/unity-catalog/tables/clinical_trials.phase3.bpx7721/export', 'POST', 200, 28500000, '91.234.99.44', 'clinical_trials', 1, TRUE),
    ('DBX-AI-012', DATEADD(SECOND, -45, CURRENT_TIMESTAMP()), 'svc-unity-rd-pipeline', '/api/2.0/mlflow/model-versions/get-download-uri', 'GET', 200, 67000000, '91.234.99.44', 'rd_pharma', 0, TRUE),
    ('DBX-AI-013', DATEADD(SECOND, -30, CURRENT_TIMESTAMP()), 'svc-unity-rd-pipeline', '/api/2.1/unity-catalog/permissions/bulk-export', 'GET', 200, 1200000, '91.234.99.44', 'rd_pharma', 0, TRUE),
    ('DBX-AI-014', DATEADD(SECOND, -15, CURRENT_TIMESTAMP()), 'svc-unity-rd-pipeline', '/api/2.0/secrets/list?scope=rd-credentials', 'GET', 200, 340000, '91.234.99.44', 'rd_pharma', 0, TRUE),
    ('DBX-AI-015', DATEADD(SECOND, -5, CURRENT_TIMESTAMP()), 'svc-unity-rd-pipeline', '/api/2.1/unity-catalog/tables/rd_pharma.compounds.admet/export', 'POST', 200, 15800000, '91.234.99.44', 'rd_pharma', 1, TRUE);

-- ── ENDPOINT_EVENTS: 10 AI Factory detections ───────────────

INSERT INTO ENDPOINT_EVENTS (event_id, hostname, event_type, severity, detection_name, risk_score, process_name, file_path, event_time)
VALUES
    ('EVT-AI-001', 'GPU-TRAIN-01', 'MALWARE', 'CRITICAL', 'Wiper.DataDestruction', 9.95, 'wiper.bin', '/tmp/.hidden/wiper.bin', CURRENT_TIMESTAMP()),
    ('EVT-AI-002', 'GPU-TRAIN-01', 'ENCRYPTION', 'CRITICAL', 'RapidEncryption.TrainingData', 9.90, 'encrypt.py', '/ai-data/training/molecular_sims/', CURRENT_TIMESTAMP()),
    ('EVT-AI-003', 'GPU-TRAIN-01', 'OUTBOUND', 'CRITICAL', 'Suspicious.Outbound.RogueIP', 9.85, 'svchost.exe', NULL, CURRENT_TIMESTAMP()),
    ('EVT-AI-004', 'MLOPS-01', 'CREDENTIAL_THEFT', 'CRITICAL', 'ServiceAccount.Credential.Stolen', 9.80, 'python3', '/opt/databricks/unity-catalog/', CURRENT_TIMESTAMP()),
    ('EVT-AI-005', 'MLOPS-01', 'DATA_EXFIL', 'CRITICAL', 'BulkExport.MLExperiments', 9.70, 'dbx-cli', NULL, CURRENT_TIMESTAMP()),
    ('EVT-AI-006', 'MLOPS-01', 'ENCRYPTION', 'HIGH', 'Experiments.Encrypted', 8.50, 'encrypt.py', '/ai-data/mlflow/experiments/', CURRENT_TIMESTAMP()),
    ('EVT-AI-007', 'AI-DATA-01', 'LATERAL_MOVEMENT', 'HIGH', 'DataLake.EncryptionSpread', 8.20, 'smb_client', '/ai-data/training/', CURRENT_TIMESTAMP()),
    ('EVT-AI-008', 'AI-DATA-01', 'FILE_SYSTEM', 'HIGH', 'MassDelete.TrainingData', 7.90, 'rm', '/ai-data/delta-lake/', CURRENT_TIMESTAMP()),
    ('EVT-AI-009', 'GPU-INF-01', 'LATERAL_MOVEMENT', 'HIGH', 'LateralSpread.ToInference', 7.50, 'smb_client', NULL, CURRENT_TIMESTAMP()),
    ('EVT-AI-010', 'GPU-INF-01', 'SERVICE_DISRUPTION', 'HIGH', 'ModelServing.Halted', 7.20, 'triton-server', '/models/BPX7721/', CURRENT_TIMESTAMP());

-- ── NETWORK_EVENTS: 20 AI Factory flows ─────────────────────

INSERT INTO NETWORK_EVENTS (event_id, source_host, source_ip, dest_ip, dest_port, protocol, bytes_sent, bytes_received, geo_country, event_time)
VALUES
    -- GPU-TRAIN-01: outbound to rogue IPs
    ('NET-AI-001', 'GPU-TRAIN-01', '10.30.1.10', '91.234.99.42', 8443, 'TCP', 245000, 18000, 'XX', CURRENT_TIMESTAMP()),
    ('NET-AI-002', 'GPU-TRAIN-01', '10.30.1.10', '91.234.99.42', 8443, 'TCP', 312000, 22000, 'XX', CURRENT_TIMESTAMP()),
    ('NET-AI-003', 'GPU-TRAIN-01', '10.30.1.10', '91.234.99.43', 443, 'TCP', 180000, 15000, 'XX', CURRENT_TIMESTAMP()),
    -- GPU-TRAIN-01: lateral movement to PowerScale
    ('NET-AI-004', 'GPU-TRAIN-01', '10.30.1.10', '10.30.2.10', 445, 'SMB', 2100000000, 1024, 'CH', CURRENT_TIMESTAMP()),
    ('NET-AI-005', 'GPU-TRAIN-01', '10.30.1.10', '10.30.2.10', 445, 'SMB', 890000000, 512, 'CH', CURRENT_TIMESTAMP()),
    -- GPU-TRAIN-01: lateral to inference server
    ('NET-AI-006', 'GPU-TRAIN-01', '10.30.1.10', '10.30.1.20', 445, 'SMB', 450000, 256, 'CH', CURRENT_TIMESTAMP()),
    -- MLOPS-01: anomalous Databricks API calls
    ('NET-AI-007', 'MLOPS-01', '10.30.3.10', '52.27.192.10', 443, 'HTTPS', 48000000, 92000, 'US', CURRENT_TIMESTAMP()),
    ('NET-AI-008', 'MLOPS-01', '10.30.3.10', '52.27.192.10', 443, 'HTTPS', 35000000, 81000, 'US', CURRENT_TIMESTAMP()),
    -- MLOPS-01: outbound to rogue IP
    ('NET-AI-009', 'MLOPS-01', '10.30.3.10', '91.234.99.44', 8443, 'TCP', 890000, 12000, 'XX', CURRENT_TIMESTAMP()),
    -- AI-DATA-01: receiving encrypted payloads from GPU-TRAIN-01
    ('NET-AI-010', 'AI-DATA-01', '10.30.2.10', '10.30.1.10', 2049, 'NFS', 128000, 2100000000, 'CH', CURRENT_TIMESTAMP()),
    -- Additional SMB lateral movement patterns
    ('NET-AI-011', 'GPU-TRAIN-01', '10.30.1.10', '10.30.2.10', 445, 'SMB', 750000000, 1024, 'CH', CURRENT_TIMESTAMP()),
    ('NET-AI-012', 'GPU-TRAIN-01', '10.30.1.10', '10.30.2.10', 445, 'SMB', 620000000, 512, 'CH', CURRENT_TIMESTAMP()),
    ('NET-AI-013', 'GPU-TRAIN-01', '10.30.1.10', '10.30.2.10', 445, 'SMB', 530000000, 256, 'CH', CURRENT_TIMESTAMP()),
    ('NET-AI-014', 'GPU-TRAIN-01', '10.30.1.10', '10.30.2.10', 445, 'SMB', 410000000, 512, 'CH', CURRENT_TIMESTAMP()),
    ('NET-AI-015', 'GPU-TRAIN-01', '10.30.1.10', '10.30.2.10', 445, 'SMB', 380000000, 256, 'CH', CURRENT_TIMESTAMP()),
    ('NET-AI-016', 'GPU-TRAIN-01', '10.30.1.10', '10.30.2.10', 445, 'SMB', 290000000, 128, 'CH', CURRENT_TIMESTAMP()),
    ('NET-AI-017', 'GPU-TRAIN-01', '10.30.1.10', '10.30.2.10', 445, 'SMB', 210000000, 256, 'CH', CURRENT_TIMESTAMP()),
    -- GPU-TRAIN-01 lateral to inference
    ('NET-AI-018', 'GPU-TRAIN-01', '10.30.1.10', '10.30.1.20', 445, 'SMB', 320000, 128, 'CH', CURRENT_TIMESTAMP()),
    ('NET-AI-019', 'GPU-TRAIN-01', '10.30.1.10', '10.30.1.20', 445, 'SMB', 280000, 256, 'CH', CURRENT_TIMESTAMP()),
    ('NET-AI-020', 'GPU-TRAIN-01', '10.30.1.10', '10.30.1.20', 445, 'SMB', 190000, 128, 'CH', CURRENT_TIMESTAMP());

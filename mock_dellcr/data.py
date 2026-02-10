"""Realistic pharma mock data for Dell Cyber Recovery simulation."""

# ── SCADA / Ransomware scenario ──────────────────────────────────────

PHARMA_FILE_PATHS = [
    "/data/scada/historian/batch_records_2025.db",
    "/data/scada/historian/temperature_logs_reactor_A3.csv",
    "/data/mes/production/lot_tracking_API_batch_7842.xml",
    "/data/lims/results/stability_study_compound_X9.xlsx",
    "/data/erp/inventory/raw_material_certificates.pdf",
    "/data/quality/deviations/deviation_2025_0891.docx",
    "/data/regulatory/submissions/eCTD_module3_specs.xml",
    "/data/scada/plc_configs/reactor_control_logic_v4.bak",
    "/data/mes/recipes/api_synthesis_route_confidential.json",
    "/data/backup/sql/pharma_gxp_database_full.bak",
    "/data/quality/sops/SOP-MFG-2025-042.pdf",
    "/data/scada/alarms/critical_events_log.dat",
]

AFFECTED_SERVERS = [
    {"name": "SCADA-HIST-01", "ip": "10.20.1.50", "role": "SCADA Historian"},
    {"name": "MES-PROD-02", "ip": "10.20.2.12", "role": "MES Production"},
    {"name": "LIMS-APP-01", "ip": "10.20.3.8", "role": "LIMS Application"},
    {"name": "ERP-DB-03", "ip": "10.20.4.22", "role": "ERP Database"},
]

# ── AI Factory scenario ──────────────────────────────────────────────

AI_FACTORY_FILE_PATHS = [
    "/ai-data/training/molecular_sims/BPX-7721_conformer_library.h5",
    "/ai-data/training/molecular_sims/docking_scores_phase3_batch.parquet",
    "/ai-data/training/protein_folding/target_3CL_ensemble_v12.pdb",
    "/ai-data/mlflow/experiments/drug_binding_affinity_exp847.pkl",
    "/ai-data/mlflow/experiments/admet_prediction_model_v3.2.pt",
    "/ai-data/mlflow/artifacts/BPX-7721_lead_optimization_final.onnx",
    "/ai-data/delta-lake/unity_catalog/pharma_rd.compound_library/",
    "/ai-data/delta-lake/unity_catalog/pharma_rd.assay_results/",
    "/ai-data/notebooks/Phase3_molecular_dynamics_pipeline.py",
    "/ai-data/notebooks/BPX-7721_toxicity_prediction.ipynb",
    "/ai-data/powerscale/snapshots/training_checkpoint_epoch_847.tar",
    "/ai-data/powerscale/inference/model_serving_BPX7721_prod.bin",
]

AI_FACTORY_SERVERS = [
    {"name": "GPU-TRAIN-01", "ip": "10.30.1.10", "role": "PowerEdge XE9680 — 8× H100 Training"},
    {"name": "GPU-INF-01", "ip": "10.30.1.20", "role": "PowerEdge R760xa — L40S Inference"},
    {"name": "AI-DATA-01", "ip": "10.30.2.10", "role": "PowerScale F710 — AI Data Lake"},
    {"name": "MLOPS-01", "ip": "10.30.3.10", "role": "Databricks MLflow + Unity Catalog"},
]

# ── Data Exfil scenario ──────────────────────────────────────────────

DATA_EXFIL_FILE_PATHS = [
    "/data/lims/results/stability_study_compound_X9.xlsx",
    "/data/mes/recipes/api_synthesis_route_confidential.json",
    "/data/regulatory/submissions/eCTD_module3_specs.xml",
    "/data/quality/deviations/deviation_2025_0891.docx",
    "/data/gxp/validation/IQ_OQ_PQ_reactor_A3.pdf",
    "/data/gxp/validation/CSV_report_lims_2025.docx",
]

DATA_EXFIL_SERVERS = [
    {"name": "LIMS-APP-01", "ip": "10.20.3.8", "role": "LIMS Application"},
    {"name": "ERP-DB-03", "ip": "10.20.4.22", "role": "ERP Database"},
]

# Map scenario type to its file paths and servers
SCENARIO_FILE_PATHS = {
    "ransomware": PHARMA_FILE_PATHS,
    "ai_factory": AI_FACTORY_FILE_PATHS,
    "data_exfil": DATA_EXFIL_FILE_PATHS,
}

SCENARIO_SERVERS = {
    "ransomware": AFFECTED_SERVERS,
    "ai_factory": AI_FACTORY_SERVERS,
    "data_exfil": DATA_EXFIL_SERVERS,
}

# Point-in-time copies available in the vault
PIT_COPIES = [
    {
        "id": "pit-2025-0207-0200",
        "timestamp": "2025-02-07T02:00:00Z",
        "status": "CLEAN",
        "size_gb": 2480,
        "label": "Pre-attack clean copy",
    },
    {
        "id": "pit-2025-0207-1400",
        "timestamp": "2025-02-07T14:00:00Z",
        "status": "CORRUPTED",
        "size_gb": 2480,
        "label": "Post-attack (encrypted files detected)",
    },
    {
        "id": "pit-2025-0206-0200",
        "timestamp": "2025-02-06T02:00:00Z",
        "status": "CLEAN",
        "size_gb": 2475,
        "label": "Daily backup - clean",
    },
]

# Vault configuration
VAULT_CONFIG = {
    "id": "vault-pharma-prod-01",
    "name": "PharmaProd-CyberVault",
    "capacity_tb": 50,
    "used_tb": 12.4,
    "policy_id": "policy-pharma-daily-01",
    "policy_name": "PharmaProd-Daily-Replication",
    "last_sync": "2025-02-07T02:15:00Z",
    "retention_days": 30,
}

# Scenario-specific threat details
SCENARIOS = {
    "ransomware": {
        "title": "Ransomware Attack on SCADA Systems",
        "description": "LockBit 4.0 ransomware detected on pharmaceutical SCADA historian servers. "
                       "Batch records and temperature logs encrypted. Production line B3 halted.",
        "severity": "critical",
        "attack_vector": "partial_encryption",
        "ransomware_family": "LockBit 4.0",
        "entry_point": "Compromised VPN credentials (phishing)",
        "iocs": [
            "SHA256: a1b2c3d4e5f6...lockbit_payload.exe",
            "Outbound: connection to rogue IP on port 443",
            "Ransom note: RESTORE-FILES.txt in 847 directories",
        ],
    },
    "ai_factory": {
        "title": "Nation-State Intrusion on AI Drug Discovery Pipeline",
        "description": "Sophisticated intrusion targeting BaselPharma R&D AI pipeline. "
                       "Stolen credentials used to access ML experiments and training data. "
                       "Molecular simulation data corrupted, GPU compute halted. "
                       "Phase III candidate BPX-7721 pipeline at risk.",
        "severity": "critical",
        "attack_vector": "credential_theft_lateral_movement",
        "ransomware_family": "NotPetya-variant (wiper + encryption)",
        "entry_point": "Stolen service account credentials",
        "iocs": [
            "SHA256: c4d5e6f7a8b9...dbx_exfil_toolkit.py",
            "API: Anomalous bulk export calls (14,000 in 3 min)",
            "Outbound: connection to rogue IP on port 8443",
            "Training data: 2.1 TB destroyed in 47 seconds",
        ],
    },
    "data_exfil": {
        "title": "Intellectual Property Exfiltration",
        "description": "Slow exfiltration of GxP validation data and synthesis routes "
                       "via covert DNS channel. 4.2 GB exfiltrated over 72 hours.",
        "severity": "high",
        "attack_vector": "dns_tunneling",
        "ransomware_family": "N/A (data theft)",
        "entry_point": "Insider threat + compromised service account",
        "iocs": [
            "Covert channel: DNS-based data exfiltration",
            "Volume: 4.2 GB over 72 hours",
            "Account: compromised service account with elevated access",
        ],
    },
}

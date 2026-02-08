"""Realistic pharma mock data for Dell Cyber Recovery simulation."""

# Pharma-specific file paths that would be on protected SCADA/MES systems
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

# Servers that appear in the CMDB
AFFECTED_SERVERS = [
    {"name": "SCADA-HIST-01", "ip": "10.20.1.50", "role": "SCADA Historian"},
    {"name": "MES-PROD-02", "ip": "10.20.2.12", "role": "MES Production"},
    {"name": "LIMS-APP-01", "ip": "10.20.3.8", "role": "LIMS Application"},
    {"name": "ERP-DB-03", "ip": "10.20.4.22", "role": "ERP Database"},
]

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
            "C2: 185.220.101.xx:443",
            "Ransom note: RESTORE-FILES.txt in 847 directories",
        ],
    },
    "supply_chain": {
        "title": "Supply Chain Compromise via SDK Update",
        "description": "Trojanized firmware update for Emerson DeltaV DCS controllers. "
                       "Backdoor implant discovered in SDK v3.8.2 update package.",
        "severity": "critical",
        "attack_vector": "supply_chain_implant",
        "ransomware_family": "N/A (APT-style backdoor)",
        "entry_point": "Compromised vendor update server",
        "iocs": [
            "SHA256: f7e8d9c0b1a2...deltav_sdk_382.msi",
            "DNS: updates.deltav-support[.]com (typosquat)",
            "Persistence: scheduled task 'DeltaVHealthCheck'",
        ],
    },
    "data_exfil": {
        "title": "Data Exfiltration via DNS Tunneling",
        "description": "Slow exfiltration of GxP validation data and API synthesis routes "
                       "via DNS TXT record queries to external C2. 4.2 GB exfiltrated over 72 hours.",
        "severity": "high",
        "attack_vector": "dns_tunneling",
        "ransomware_family": "N/A (data theft)",
        "entry_point": "Insider threat + compromised service account",
        "iocs": [
            "DNS: *.data.pharma-analytics[.]xyz (exfil channel)",
            "Volume: 4.2 GB encoded in 2.1M DNS queries",
            "Account: svc_lims_readonly (privilege escalation)",
        ],
    },
}

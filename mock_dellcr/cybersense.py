"""CyberSense ML analysis simulation.

Generates realistic forensic results matching real CyberSense output format:
confidence scores, corrupted file lists, attack vector classification.
"""

from datetime import datetime
from mock_dellcr.data import (
    SCENARIO_FILE_PATHS,
    SCENARIO_SERVERS,
    PHARMA_FILE_PATHS,
    AFFECTED_SERVERS,
    PIT_COPIES,
    SCENARIOS,
)


def generate_analysis(scenario_type: str = "ransomware") -> dict:
    """Generate a CyberSense analysis report for the given scenario.

    Returns data matching the real CyberSense output structure.
    Uses scenario-specific file paths and servers.
    """
    scenario = SCENARIOS.get(scenario_type, SCENARIOS["ransomware"])
    file_paths = SCENARIO_FILE_PATHS.get(scenario_type, PHARMA_FILE_PATHS)
    servers = SCENARIO_SERVERS.get(scenario_type, AFFECTED_SERVERS)

    # Find the last clean PIT copy
    clean_pits = [p for p in PIT_COPIES if p["status"] == "CLEAN"]
    last_clean = clean_pits[0] if clean_pits else PIT_COPIES[0]

    corrupted_count = len(file_paths)
    total_scanned = corrupted_count * 142  # Realistic ratio

    # AI Factory scenario has larger data at risk (training data is huge)
    data_at_risk_gb = 2100.0 if scenario_type == "ai_factory" else 248.7

    return {
        "analysis_id": f"cs-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "COMPLETE",
        "confidence": 99.99,
        "verdict": "CORRUPTION_DETECTED",
        "summary": {
            "total_files_scanned": total_scanned,
            "total_corrupted": corrupted_count,
            "corruption_rate": round(corrupted_count / total_scanned * 100, 2),
            "data_at_risk_gb": data_at_risk_gb,
        },
        "attack_classification": {
            "vector": scenario["attack_vector"],
            "family": scenario["ransomware_family"],
            "entry_point": scenario["entry_point"],
            "first_seen": "2025-02-07T11:23:47Z",
            "iocs": scenario["iocs"],
        },
        "corrupted_files": [
            {
                "path": path,
                "original_hash": f"sha256:{'a' * 16}...orig",
                "current_hash": f"sha256:{'f' * 16}...enc",
                "entropy_score": 7.98,  # High entropy = encrypted
                "detection": "entropy_anomaly",
            }
            for path in file_paths
        ],
        "affected_systems": [
            {
                "hostname": srv["name"],
                "ip": srv["ip"],
                "role": srv["role"],
                "status": "COMPROMISED",
            }
            for srv in servers
        ],
        "recovery_recommendation": {
            "action": "RESTORE_FROM_PIT",
            "pit_id": last_clean["id"],
            "pit_timestamp": last_clean["timestamp"],
            "pit_label": last_clean["label"],
            "estimated_recovery_time_min": 45,
        },
    }

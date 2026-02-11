"""Pre-written direction cues for each (scenario, step, status) combination.

The playbook provides instant (0ms latency) presenter cues for known scenarios.
The LLM layer is only invoked for edge cases or Scenarist-generated scenarios
that have no playbook entries.
"""


# Cue structure: {current_cue, talking_points, next_cues, timing}
# timing: "go" (green), "wait" (amber), "pause" (red)

PLAYBOOKS = {
    "ransomware": {
        ("DETECT", "running"): {
            "cue": "Watch the attack feed cascade on the left",
            "talking_points": [
                "Snowflake AI is scanning 20+ network flows and 10 endpoint events in real time",
                "This is what your SOC team sees at 2 AM — except the AI catches it in seconds",
                "Notice the threat scores: 9.87/10 on the historian server",
            ],
            "next_cues": ["Step completes automatically", "Snowflake pause screen next"],
            "timing": "go",
        },
        ("DETECT", "complete"): {
            "cue": "Detection complete — highlight the threat score",
            "talking_points": [
                "AI detected LockBit 4.0 across 4 hosts with 99%+ confidence",
                "Traditional SIEM? Hours. Snowflake ML? Seconds.",
                "This is the difference between losing 1 day vs 1 month of production",
            ],
            "next_cues": ["Snowflake worksheet pause coming up"],
            "timing": "wait",
        },
        ("PAUSE", "complete"): {
            "cue": "PAUSE — Open Snowflake worksheet and walk through the queries",
            "talking_points": [
                "Show the audience the actual Snowflake queries that detected the threat",
                "Point out the anomaly scores and contributing factors",
                "This is real Snowflake — not a mock. The data is queryable right now.",
            ],
            "next_cues": ["Click Continue when ready to proceed to incident creation"],
            "timing": "pause",
        },
        ("INCIDENT", "running"): {
            "cue": "ServiceNow incident is being created in real time",
            "talking_points": [
                "Automatic incident creation — no manual ticket filing",
                "Priority 1, Category: Malware — fully classified from AI detection",
                "Your SOC team gets notified immediately",
            ],
            "next_cues": ["Incident card appears on dashboard", "ServiceNow pause next"],
            "timing": "go",
        },
        ("INCIDENT", "complete"): {
            "cue": "Incident created — point to the ServiceNow card",
            "talking_points": [
                "Real ServiceNow incident with full details",
                "This is your audit trail — critical for FDA compliance",
                "Every action from here is logged against this incident number",
            ],
            "next_cues": ["ServiceNow pause — open the incident in a new tab"],
            "timing": "wait",
        },
        ("VAULT SYNC", "running"): {
            "cue": "Dell Cyber Recovery vault sync starting — this is the air gap",
            "talking_points": [
                "The vault is physically isolated — air-gapped from production",
                "Even if the attacker owns your entire network, they cannot touch the vault",
                "This is the insurance policy — and it's replicating right now",
            ],
            "next_cues": ["Vault sync completes in ~10 seconds", "CyberSense analysis next"],
            "timing": "go",
        },
        ("VAULT SYNC", "complete"): {
            "cue": "Vault sealed — air gap closed",
            "talking_points": [
                "Data is now safe in the isolated vault",
                "CyberSense ML will now analyze the copy for corruption",
            ],
            "next_cues": ["CyberSense analysis starting"],
            "timing": "go",
        },
        ("CYBERSENSE", "running"): {
            "cue": "CyberSense ML analysis in progress — this is the magic",
            "talking_points": [
                "CyberSense uses 200+ analytics to detect corruption",
                "Not just signature-based — ML detects novel ransomware variants",
                "It's analyzing billions of data points in the vault copy",
            ],
            "next_cues": ["Analysis completes with corruption report"],
            "timing": "go",
        },
        ("CYBERSENSE", "complete"): {
            "cue": "CORRUPTION DETECTED — point to the confidence score",
            "talking_points": [
                "99.99% confidence — CyberSense identified the exact corruption",
                "It also found the last clean point-in-time copy",
                "This is the difference: without CyberSense you restore from a backup that might also be encrypted",
            ],
            "next_cues": ["Forensics report coming up"],
            "timing": "wait",
        },
        ("FORENSICS", "complete"): {
            "cue": "Forensics complete — walk through the CyberSense report",
            "talking_points": [
                "Corrupted files identified with exact paths",
                "Attack vector and ransomware family classified",
                "Clean PIT copy identified for recovery",
                "Work notes automatically posted to ServiceNow for the audit trail",
            ],
            "next_cues": ["Recovery starting next"],
            "timing": "wait",
        },
        ("RECOVER", "running"): {
            "cue": "Recovery in progress — restoring from clean copy",
            "talking_points": [
                "Restoring from the known-clean point-in-time copy",
                "This is surgical recovery — only corrupted files are replaced",
                "Production can resume within hours, not weeks",
            ],
            "next_cues": ["Recovery progress bar filling", "Resolution next"],
            "timing": "go",
        },
        ("RECOVER", "complete"): {
            "cue": "Recovery complete — all files restored",
            "talking_points": [
                "1,704 files restored from clean PIT copy",
                "Production line B3 can restart immediately",
                "Total recovery time: minutes, not weeks",
                "Without this? 2-4 weeks down, $50-100M total impact",
            ],
            "next_cues": ["ServiceNow resolution next"],
            "timing": "wait",
        },
        ("RESOLVE", "complete"): {
            "cue": "Incident resolved — full audit trail in ServiceNow",
            "talking_points": [
                "Complete forensic report attached to the incident",
                "FDA-ready audit trail from detection to recovery",
                "No ransom paid. No data lost. Production restored.",
                "THIS is what Dell Cyber Recovery delivers.",
            ],
            "next_cues": ["Closing message"],
            "timing": "go",
        },
        ("COMPLETE", "complete"): {
            "cue": "Demo complete — deliver the closing message",
            "talking_points": [
                "Zero Trust Cyber Recovery: peace of mind for the CISO, proven plan for the CIO",
                "Business continuity for the lines of business",
                "It pays for itself the day you need it",
                "Ask: 'Which business areas should we protect first?'",
            ],
            "next_cues": [],
            "timing": "go",
        },
    },

    # AI Factory scenario — abbreviated playbook (extends ransomware pattern)
    "ai_factory": {
        ("DETECT", "running"): {
            "cue": "Watch the AI Factory attack cascade — R&D pipeline under siege",
            "talking_points": [
                "Nation-state APT targeting the drug discovery pipeline",
                "This is IP theft + destruction — the crown jewels of pharma",
                "$2.1B Phase III candidate at risk",
            ],
            "next_cues": ["Detection completes", "Snowflake SIEM analysis"],
            "timing": "go",
        },
        ("DETECT", "complete"): {
            "cue": "AI pipeline compromise detected — highlight the Databricks damage",
            "talking_points": [
                "ML experiments encrypted, training data corrupted",
                "GPU cluster halted — $50K/day in compute alone",
                "This is not just IT — this is R&D extinction",
            ],
            "next_cues": ["Snowflake pause for SIEM walkthrough"],
            "timing": "wait",
        },
        ("COMPLETE", "complete"): {
            "cue": "Demo complete — close with AI Factory recovery message",
            "talking_points": [
                "Dell AI Factory + Cyber Recovery = protected AI pipeline",
                "PowerScale stores the data, Cyber Recovery protects it",
                "Without this: 6-12 months to retrain, $200M+ in delayed trials",
                "Ask: 'How is your AI pipeline protected today?'",
            ],
            "next_cues": [],
            "timing": "go",
        },
    },

    # Data exfil scenario — abbreviated playbook
    "data_exfil": {
        ("DETECT", "running"): {
            "cue": "Watch the DNS exfiltration alerts cascade",
            "talking_points": [
                "This is the silent killer — 72 hours of covert data theft",
                "GxP validation data and synthesis routes exfiltrated",
                "Your competitors now have your formulations",
            ],
            "next_cues": ["Detection with exfil volume details"],
            "timing": "go",
        },
        ("DETECT", "complete"): {
            "cue": "4.2 GB exfiltrated — highlight the regulatory exposure",
            "talking_points": [
                "847 patient records exposed — immediate GDPR/HIPAA notification required",
                "FDA 21 CFR Part 11 violation — consent decree territory",
                "The data is gone, but we can prove what was taken and when",
            ],
            "next_cues": ["Snowflake analysis of DNS traffic patterns"],
            "timing": "wait",
        },
        ("COMPLETE", "complete"): {
            "cue": "Demo complete — close with data protection message",
            "talking_points": [
                "CyberSense detected the exfil that traditional tools missed",
                "Complete forensic timeline for regulatory reporting",
                "Air-gapped vault preserved the original, uncompromised data",
                "Ask: 'How would you report a 72-hour exfil to the FDA today?'",
            ],
            "next_cues": [],
            "timing": "go",
        },
    },
}


def get_cue(scenario: str, step_name: str, status: str) -> dict | None:
    """Look up a playbook cue for the given scenario/step/status.

    Returns None if no playbook entry exists (Director falls back to LLM).
    """
    scenario_playbook = PLAYBOOKS.get(scenario, {})
    return scenario_playbook.get((step_name, status))

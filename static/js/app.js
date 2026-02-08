/**
 * CyberDemo — Alpine.js dashboard component.
 *
 * Manages the 7-step scenario workflow via SSE, tracks vault state,
 * incident data, and forensic results for real-time UI updates.
 */

// Pre-defined attack event sequences per scenario.
// These cascade visually during the DETECT phase to give the audience
// a "SOC alert feed" experience before recovery kicks in.
const ATTACK_SEQUENCES = {
    ransomware: [
        { severity: "HIGH",     system: "EMAIL-GW",       message: "Phishing payload opened by svc_scada@baselpharma.com" },
        { severity: "HIGH",     system: "AD-DC01",        message: "Kerberoasting detected — service account credential harvested" },
        { severity: "CRITICAL", system: "SCADA-HIST-01",  message: "LockBit 4.0 payload deployed on historian server" },
        { severity: "CRITICAL", system: "MES-PRIMARY",    message: "Lateral movement — batch record database encrypted" },
        { severity: "CRITICAL", system: "LINE-B3-PLC",    message: "Production line B3 HALTED — temperature monitoring offline" },
        { severity: "BUSINESS", system: "IMPACT",         message: "Estimated impact: $500K–$2M/day — FDA 483 risk if batch records unrecoverable" },
    ],
    ai_factory: [
        { severity: "HIGH",     system: "DATABRICKS-SP",  message: "OAuth token theft — service principal credential exfiltrated" },
        { severity: "HIGH",     system: "UNITY-CATALOG",  message: "Unauthorized access to ML experiment metadata" },
        { severity: "CRITICAL", system: "POWERSCALE-AI",  message: "Training data corrupted — molecular simulation poisoned" },
        { severity: "CRITICAL", system: "MLFLOW-REG",     message: "Model artifacts encrypted on PowerScale data lake" },
        { severity: "CRITICAL", system: "XE9680-GPU-01",  message: "GPU cluster compute jobs terminated — pipeline halted" },
        { severity: "BUSINESS", system: "IMPACT",         message: "Phase III candidate BPX-7721 ($2.1B pipeline) compromised" },
    ],
    data_exfil: [
        { severity: "HIGH",     system: "DNS-PROXY",      message: "Anomalous DNS TXT queries from svc_lims_readonly (148/min)" },
        { severity: "HIGH",     system: "LIMS-DB-01",     message: "GxP validation data accessed — bulk SELECT on batch_records" },
        { severity: "CRITICAL", system: "ERP-CHEM",       message: "API synthesis routes exfiltrated — 2.1 GB encoded in DNS" },
        { severity: "CRITICAL", system: "CLINICAL-DW",    message: "Patient trial data accessed — 847 subject records" },
        { severity: "CRITICAL", system: "DNS-PROXY",      message: "Total exfiltration: 4.2 GB over 72 hours via DNS tunnel" },
        { severity: "BUSINESS", system: "IMPACT",         message: "FDA 21 CFR Part 11 violation — consent decree and $50M+ exposure" },
    ],
};

function cyberDemo() {
    return {
        // --- State ---
        running: false,
        currentStep: 0,
        scenarioType: null,
        attackEvents: [],       // Cascaded attack + remediation indicators
        feedPhase: "attack",    // "attack" | "recovery" | "resolved" — drives panel header
        paused: false,          // True when waiting for presenter to review ServiceNow
        pauseIncidentUrl: "",   // ServiceNow incident URL to open during pause

        // Step definitions (labels shown in the timeline)
        stepDefs: [
            { name: "DETECT",     waiting: "Waiting for threat detection..." },
            { name: "INCIDENT",   waiting: "Waiting to create incident..." },
            { name: "VAULT SYNC", waiting: "Waiting for vault sync..." },
            { name: "CYBERSENSE", waiting: "Waiting for analysis..." },
            { name: "FORENSICS",  waiting: "Waiting for forensics..." },
            { name: "RECOVER",    waiting: "Waiting for recovery..." },
            { name: "RESOLVE",    waiting: "Waiting for resolution..." },
        ],

        // Live step data (indexed 0-6, populated by SSE events)
        steps: {},

        // Vault state for the air gap visualization
        vaultState: "IDLE",

        // ServiceNow incident data
        incident: {
            number: "",
            sys_id: "",
            url: "",
            state: "",
            mode: "",
            priority: "",
            category: "",
            description: "",
        },

        // CyberSense forensics data
        forensics: {
            confidence: 0,
            corrupted_count: 0,
            attack_vector: "",
            family: "",
            clean_pit: "",
            affected_systems: [],
        },

        // Recovery progress
        recovery: {
            pit_id: "",
            restored_files: 0,
            progress: 0,
        },

        // Snowflake AI detection results
        snowflakeDetection: {
            threat_score: 0,
            threat_count: 0,
            primary_host: "",
            summary: {},
            threats: [],
            model_version: "",
        },

        // Connectivity status
        snowAvailable: false,
        dellcrAvailable: false,
        snowflakeAvailable: false,

        // --- Methods ---

        /** Check connectivity to ServiceNow and Dell CR. */
        async checkStatus() {
            try {
                const resp = await fetch("/api/status");
                if (resp.ok) {
                    const data = await resp.json();
                    this.snowAvailable = data.servicenow?.available || false;
                    this.dellcrAvailable = data.dell_cr?.available || false;
                    this.snowflakeAvailable = data.snowflake?.available || false;
                    this.updateStatusIndicators();
                }
            } catch (e) {
                console.warn("Status check failed:", e);
            }
        },

        /** Update the header status dots. */
        updateStatusIndicators() {
            const indicators = {
                "snowflake-status": this.snowflakeAvailable,
                "snow-status": this.snowAvailable,
                "dellcr-status": this.dellcrAvailable,
            };
            for (const [id, available] of Object.entries(indicators)) {
                const el = document.getElementById(id);
                if (el) {
                    const dot = el.querySelector("span:first-child");
                    dot.className = "w-2 h-2 rounded-full " +
                        (available ? "bg-emerald-400" : "bg-gray-600");
                }
            }
        },

        /** Start a scenario — opens an SSE connection to the backend. */
        startScenario(type) {
            if (this.running) return;

            // Reset state
            this.running = true;
            this.currentStep = 0;
            this.scenarioType = type;
            this.steps = {};
            this.attackEvents = [];
            this.feedPhase = "attack";
            this.paused = false;
            this.pauseIncidentUrl = "";
            this.vaultState = "IDLE";
            this.incident = { number: "", sys_id: "", url: "", state: "", mode: "", priority: "", category: "", description: "" };
            this.forensics = { confidence: 0, corrupted_count: 0, attack_vector: "", family: "", clean_pit: "", affected_systems: [] };
            this.recovery = { pit_id: "", restored_files: 0, progress: 0 };
            this.snowflakeDetection = { threat_score: 0, threat_count: 0, primary_host: "", summary: {}, threats: [], model_version: "" };

            // Cascade attack events with staggered delays (plays during DETECT phase)
            const sequence = ATTACK_SEQUENCES[type] || [];
            sequence.forEach((event, i) => {
                setTimeout(() => {
                    this.attackEvents.push({
                        ...event,
                        time: new Date().toLocaleTimeString("en-US", { hour12: false }),
                    });
                }, 600 + i * 800);
            });

            // POST to trigger scenario, then read SSE stream
            fetch("/api/scenario", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ type: type }),
            }).then(response => {
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = "";

                const readStream = () => {
                    reader.read().then(({ done, value }) => {
                        if (done) {
                            this.running = false;
                            return;
                        }

                        buffer += decoder.decode(value, { stream: true });

                        // Parse SSE lines from buffer
                        const lines = buffer.split("\n");
                        buffer = lines.pop() || ""; // keep incomplete last line

                        for (const line of lines) {
                            if (line.startsWith("data: ")) {
                                try {
                                    const event = JSON.parse(line.slice(6));
                                    this.handleSSEEvent(event);
                                } catch (e) {
                                    // Skip malformed lines
                                }
                            }
                        }

                        readStream();
                    }).catch(err => {
                        console.error("SSE stream error:", err);
                        this.running = false;
                    });
                };

                readStream();
            }).catch(err => {
                console.error("Scenario request failed:", err);
                this.running = false;
            });
        },

        /** Process a single SSE event and update UI state. */
        handleSSEEvent(event) {
            const idx = event.step - 1; // 0-indexed
            this.currentStep = event.step;

            // Store step data
            this.steps[idx] = {
                status: event.status,
                message: event.message,
                timestamp: event.timestamp,
                data: event.data || {},
            };

            // Force Alpine reactivity by reassigning the object
            this.steps = { ...this.steps };

            // Update derived state based on step
            this.updateDerivedState(event);
        },

        /** Update vault, incident, forensics state from step events. */
        updateDerivedState(event) {
            const data = event.data || {};

            switch (event.name) {
                case "DETECT":
                    if (event.status === "complete") {
                        this.incident.priority = data.priority || "1";
                        this.incident.category = data.category || "";
                        // Populate Snowflake detection panel
                        if (data.source === "snowflake") {
                            this.snowflakeDetection = {
                                threat_score: data.threat_score || 0,
                                threat_count: data.threat_count || 0,
                                primary_host: data.primary_host || "",
                                summary: data.summary || {},
                                threats: data.threats || [],
                                model_version: data.model_version || "",
                            };
                        }
                    }
                    break;

                case "INCIDENT":
                    if (event.status === "complete") {
                        this.incident.number = data.number || "";
                        this.incident.sys_id = data.sys_id || "";
                        this.incident.url = data.url || "";
                        this.incident.mode = data.mode || "mock";
                        this.incident.state = "New";
                        this.incident.description = this.getScenarioDescription();
                    }
                    break;

                case "VAULT SYNC":
                    if (event.status === "running") {
                        this.vaultState = "SYNCING";
                        this.feedPhase = "recovery";
                        this.pushFeedEvent("RECOVERY", "CR VAULT", "Air gap opened — replicating production data to isolated vault");
                    } else if (event.status === "complete") {
                        this.vaultState = data.vault_state || "LOCKED";
                        this.pushFeedEvent("RECOVERY", "CR VAULT", "Vault sync complete — air gap sealed, data secured");
                    }
                    break;

                case "CYBERSENSE":
                    if (event.status === "running") {
                        this.vaultState = "ANALYZING";
                        this.pushFeedEvent("RECOVERY", "CYBERSENSE", "ML analysis scanning vault copy for corruption signatures...");
                    } else if (event.status === "complete") {
                        this.forensics.confidence = data.confidence || 99.99;
                        this.vaultState = "CORRUPTED";
                        this.pushFeedEvent("RECOVERY", "CYBERSENSE",
                            "Corruption detected — " + (data.confidence || 99.99) + "% confidence, clean PIT copy identified");
                    }
                    break;

                case "FORENSICS":
                    if (event.status === "complete") {
                        this.forensics.corrupted_count = data.corrupted_count || 0;
                        this.forensics.attack_vector = data.attack_vector || "";
                        this.forensics.family = data.family || "";
                        this.forensics.clean_pit = data.clean_pit || "";
                        this.forensics.affected_systems = data.affected_systems || [];
                        this.pushFeedEvent("RECOVERY", "FORENSICS",
                            (data.corrupted_count || 0) + " corrupted files identified — attack vector: " +
                            (data.family || "unknown") + " (" + (data.attack_vector || "N/A") + ")");
                    }
                    break;

                case "RECOVER":
                    if (event.status === "running") {
                        this.vaultState = "RECOVERING";
                        this.recovery.pit_id = data.pit_id || "";
                        this.recovery.progress = 50;
                        this.pushFeedEvent("RECOVERY", "RESTORE", "Restoring from clean PIT copy " + (data.pit_id || ""));
                    } else if (event.status === "complete") {
                        this.vaultState = "RECOVERED";
                        this.recovery.pit_id = data.pit_id || "";
                        this.recovery.restored_files = data.restored_files || 0;
                        this.recovery.progress = 100;
                        this.pushFeedEvent("RESOLVED", "RESTORE",
                            "Recovery complete — " + (data.restored_files || 0) + " files restored from clean copy");
                    }
                    break;

                case "RESOLVE":
                    if (event.status === "complete") {
                        this.incident.state = "Resolved";
                        this.feedPhase = "resolved";
                        this.pushFeedEvent("RESOLVED", "SERVICENOW",
                            "Incident " + (data.number || this.incident.number) + " resolved — all systems operational");
                    }
                    break;

                case "PAUSE":
                    // Presenter pause — show "View Incident" / "Continue" button
                    this.paused = true;
                    this.pauseIncidentUrl = data.incident_url || "";
                    break;

                case "COMPLETE":
                    this.running = false;
                    break;
            }
        },

        /** Open ServiceNow incident in new tab, then resume the scenario. */
        async handlePauseAction() {
            if (this.pauseIncidentUrl) {
                // First click: open ServiceNow
                window.open(this.pauseIncidentUrl, '_blank');
                // Clear the URL so next click triggers resume
                this.pauseIncidentUrl = "";
            } else {
                // Second click: tell the backend to continue
                this.paused = false;
                await fetch("/api/scenario/resume", { method: "POST" });
            }
        },

        /** Get scenario description for the incident card. */
        getScenarioDescription() {
            const descriptions = {
                ransomware: "Ransomware detected on pharmaceutical SCADA systems. Batch records and temperature logs encrypted on SCADA-HIST-01. Production line B3 halted.",
                ai_factory: "APT compromise of R&D AI Factory. Databricks service principal stolen — MLflow experiments encrypted, molecular simulation data corrupted on PowerScale. Phase III candidate BPX-7721 at risk.",
                data_exfil: "Slow exfiltration of GxP validation data and API synthesis routes detected via DNS TXT record queries. 4.2 GB exfiltrated over 72 hours.",
            };
            return descriptions[this.scenarioType] || "";
        },

        /** Push a remediation event into the attack feed during recovery. */
        pushFeedEvent(severity, system, message) {
            this.attackEvents.push({
                severity,
                system,
                message,
                time: new Date().toLocaleTimeString("en-US", { hour12: false }),
            });
        },

        /** Format ISO timestamp to HH:MM:SS for the timeline. */
        formatTime(isoStr) {
            if (!isoStr) return "";
            try {
                const d = new Date(isoStr);
                return d.toLocaleTimeString("en-US", { hour12: false });
            } catch {
                return "";
            }
        },
    };
}

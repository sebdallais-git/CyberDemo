/**
 * CyberDemo — Alpine.js dashboard component.
 *
 * Manages the 7-step scenario workflow via SSE, tracks vault state,
 * incident data, and forensic results for real-time UI updates.
 */
function cyberDemo() {
    return {
        // --- State ---
        running: false,
        currentStep: 0,
        scenarioType: null,

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
            this.vaultState = "IDLE";
            this.incident = { number: "", sys_id: "", url: "", state: "", mode: "", priority: "", category: "", description: "" };
            this.forensics = { confidence: 0, corrupted_count: 0, attack_vector: "", family: "", clean_pit: "", affected_systems: [] };
            this.recovery = { pit_id: "", restored_files: 0, progress: 0 };
            this.snowflakeDetection = { threat_score: 0, threat_count: 0, primary_host: "", summary: {}, threats: [], model_version: "" };

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
                    } else if (event.status === "complete") {
                        this.vaultState = data.vault_state || "LOCKED";
                    }
                    break;

                case "CYBERSENSE":
                    if (event.status === "running") {
                        this.vaultState = "ANALYZING";
                    } else if (event.status === "complete") {
                        this.forensics.confidence = data.confidence || 99.99;
                        this.vaultState = "CORRUPTED";
                    }
                    break;

                case "FORENSICS":
                    if (event.status === "complete") {
                        this.forensics.corrupted_count = data.corrupted_count || 0;
                        this.forensics.attack_vector = data.attack_vector || "";
                        this.forensics.family = data.family || "";
                        this.forensics.clean_pit = data.clean_pit || "";
                        this.forensics.affected_systems = data.affected_systems || [];
                    }
                    break;

                case "RECOVER":
                    if (event.status === "running") {
                        this.vaultState = "RECOVERING";
                        this.recovery.pit_id = data.pit_id || "";
                        this.recovery.progress = 50;
                    } else if (event.status === "complete") {
                        this.vaultState = "RECOVERED";
                        this.recovery.pit_id = data.pit_id || "";
                        this.recovery.restored_files = data.restored_files || 0;
                        this.recovery.progress = 100;
                    }
                    break;

                case "RESOLVE":
                    if (event.status === "complete") {
                        this.incident.state = "Resolved";
                    }
                    break;

                case "COMPLETE":
                    this.running = false;
                    break;
            }
        },

        /** Get scenario description for the incident card. */
        getScenarioDescription() {
            const descriptions = {
                ransomware: "Ransomware detected on pharmaceutical SCADA systems. Batch records and temperature logs encrypted on SCADA-HIST-01. Production line B3 halted.",
                supply_chain: "Backdoor implant discovered in Emerson DeltaV SDK v3.8.2 update. Compromised vendor update server pushed malicious firmware to DCS controllers.",
                data_exfil: "Slow exfiltration of GxP validation data and API synthesis routes detected via DNS TXT record queries. 4.2 GB exfiltrated over 72 hours.",
            };
            return descriptions[this.scenarioType] || "";
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

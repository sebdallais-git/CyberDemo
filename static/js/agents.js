/**
 * CyberDemo Agents — Alpine.js components for agent UIs.
 *
 * Contains:
 * - directorMixin: SSE client for Director panel (injected into cyberDemo)
 * - agentHub(): Agent hub page component
 * - scenaristForm(): Scenarist form component
 * - documentalistForm(): Documentalist form component
 * - customerForm(): Customer evaluator form component
 * - recruiterForm(): Recruiter form component
 */

// ── Director Mixin (added to cyberDemo component) ──────────────

const directorMixin = {
    directorEnabled: false,
    directorCue: { cue: "", talking_points: [], next_cues: [], timing: "standby" },
    directorHistory: [],
    _directorReader: null,

    toggleDirector() {
        this.directorEnabled = !this.directorEnabled;
        if (this.directorEnabled && this.running && this.scenarioType) {
            this.startDirectorStream(this.scenarioType);
        } else if (!this.directorEnabled) {
            this.stopDirectorStream();
        }
    },

    startDirectorStream(scenario) {
        if (this._directorReader) return;

        fetch(`/api/agents/director/stream?scenario=${scenario}`).then(response => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";
            this._directorReader = reader;

            const readStream = () => {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        this._directorReader = null;
                        return;
                    }

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split("\n");
                    buffer = lines.pop() || "";

                    for (const line of lines) {
                        if (line.startsWith("data: ")) {
                            try {
                                const cue = JSON.parse(line.slice(6));
                                // Push current cue to history before replacing
                                if (this.directorCue.cue) {
                                    this.directorHistory.push({ ...this.directorCue });
                                }
                                this.directorCue = cue;
                            } catch (e) {
                                // Skip malformed lines
                            }
                        }
                    }

                    readStream();
                }).catch(() => {
                    this._directorReader = null;
                });
            };

            readStream();
        }).catch(err => {
            console.warn("Director stream failed:", err);
        });
    },

    stopDirectorStream() {
        if (this._directorReader) {
            this._directorReader.cancel();
            this._directorReader = null;
        }
    },
};


// ── Agent Hub Component ─────────────────────────────────────────

function agentHub() {
    return {
        agents: [
            {
                name: "Scenarist",
                description: "Generate new scenarios from news or curated input",
                icon: "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
                href: "/agents/scenarist",
                color: "emerald",
            },
            {
                name: "Documentalist",
                description: "Generate code docs or scenario runbooks",
                icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
                href: "/agents/documentalist",
                color: "blue",
            },
            {
                name: "Customer",
                description: "Evaluate scenarios from CIO/CFO/R&D/MFG perspectives",
                icon: "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z",
                href: "/agents/customer",
                color: "amber",
            },
            {
                name: "Recruiter",
                description: "Simulate talent scout interviews and fit reports",
                icon: "M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z",
                href: "/agents/recruiter",
                color: "purple",
            },
        ],
    };
}


// ── Scenarist Form Component ────────────────────────────────────

function scenaristForm() {
    return {
        mode: "search",
        topic: "pharma ransomware attack 2025",
        curatedText: "",
        urls: "",
        scenarioName: "",
        running: false,
        result: "",
        status: "",

        async submit() {
            this.running = true;
            this.result = "";
            this.status = "running";

            const body = {
                mode: this.mode,
                topic: this.topic,
                curated_text: this.curatedText,
                urls: this.urls ? this.urls.split("\n").filter(u => u.trim()) : [],
                scenario_name: this.scenarioName,
            };

            try {
                const resp = await fetch("/api/agents/scenarist/run", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(body),
                });
                await this._readSSE(resp);
            } catch (e) {
                this.status = "error";
                this.result = "Request failed: " + e.message;
            }
            this.running = false;
        },

        async _readSSE(resp) {
            const reader = resp.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop() || "";
                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            this.status = data.status;
                            if (data.result) this.result = data.result;
                            else if (data.message) this.result = data.message;
                        } catch (e) { /* skip */ }
                    }
                }
            }
        },
    };
}


// ── Documentalist Form Component ────────────────────────────────

function documentalistForm() {
    return {
        mode: "code",
        scenario: "ransomware",
        running: false,
        result: "",
        status: "",

        async submit() {
            this.running = true;
            this.result = "";
            this.status = "running";

            try {
                const resp = await fetch("/api/agents/documentalist/run", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ mode: this.mode, scenario: this.scenario }),
                });
                await this._readSSE(resp);
            } catch (e) {
                this.status = "error";
                this.result = "Request failed: " + e.message;
            }
            this.running = false;
        },

        async _readSSE(resp) {
            const reader = resp.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop() || "";
                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            this.status = data.status;
                            if (data.result) this.result = data.result;
                            else if (data.message) this.result = data.message;
                        } catch (e) { /* skip */ }
                    }
                }
            }
        },
    };
}


// ── Customer Form Component ─────────────────────────────────────

function customerForm() {
    return {
        scenario: "ransomware",
        persona: "all",
        running: false,
        result: "",
        status: "",

        async submit() {
            this.running = true;
            this.result = "";
            this.status = "running";

            try {
                const resp = await fetch("/api/agents/customer/run", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ scenario: this.scenario, persona: this.persona }),
                });
                await this._readSSE(resp);
            } catch (e) {
                this.status = "error";
                this.result = "Request failed: " + e.message;
            }
            this.running = false;
        },

        async _readSSE(resp) {
            const reader = resp.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop() || "";
                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            this.status = data.status;
                            if (data.result) this.result = data.result;
                            else if (data.message) this.result = data.message;
                        } catch (e) { /* skip */ }
                    }
                }
            }
        },
    };
}


// ── Recruiter Form Component ────────────────────────────────────

function recruiterForm() {
    return {
        company: "snowflake",
        mode: "report",
        running: false,
        result: "",
        status: "",

        async submit() {
            this.running = true;
            this.result = "";
            this.status = "running";

            try {
                const resp = await fetch("/api/agents/recruiter/run", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ company: this.company, mode: this.mode }),
                });
                await this._readSSE(resp);
            } catch (e) {
                this.status = "error";
                this.result = "Request failed: " + e.message;
            }
            this.running = false;
        },

        async _readSSE(resp) {
            const reader = resp.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop() || "";
                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            this.status = data.status;
                            if (data.result) this.result = data.result;
                            else if (data.message) this.result = data.message;
                        } catch (e) { /* skip */ }
                    }
                }
            }
        },
    };
}

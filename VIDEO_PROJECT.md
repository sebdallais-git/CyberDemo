# CyberDemo — LinkedIn Video Production Guide

## Overview
- **Format:** Screen recording + voiceover (you reading the script)
- **Duration:** 90–120 seconds (LinkedIn sweet spot)
- **Tone:** Confident, technical but accessible. You're a Dell GAM showing what's possible.
- **Angle:** "Here's what an automated cyber recovery workflow looks like for pharma"
- **Resolution:** Record at 1920x1080, export 1080x1080 (square) for LinkedIn feed

---

## Pre-Recording Setup

### Browser Tabs (open these BEFORE recording)
1. **Tab 1:** CyberDemo Dashboard — `http://100.111.151.186:8889`
2. **Tab 2:** Snowflake Console — `https://ynjslux-yg03351.snowflakecomputing.com` (logged in, navigate to CYBER_SECURITY > SIEM > ANOMALY_SCORES table preview)
3. **Tab 3:** ServiceNow — `https://dev275414.service-now.com/incident_list.do` (logged in, incident list view)

### Dashboard Prep
- Make sure no scenario is running (refresh the page)
- All 3 status dots should be GREEN (Snowflake, ServiceNow, Dell CR)
- Browser zoom: 110% looks good on video

### Recording Tool
- Use QuickTime (Cmd+Shift+5) or OBS
- Record the full screen, crop later
- Use a separate mic if possible (AirPods Pro work fine)

---

## SCRIPT & SHOT LIST

### SCENE 1 — HOOK (0:00–0:10)
**[ON SCREEN: Dashboard, idle state, all green dots visible in header]**

> "What happens when ransomware hits your pharmaceutical production line at 2 AM? Let me show you a fully automated detection-to-recovery workflow — running live, right now."

**Direction:** Camera is on the dashboard. Slowly mouse over the 3 green status indicators as you say "running live."

---

### SCENE 2 — SET THE STAGE (0:10–0:22)

**[ON SCREEN: Still on dashboard, mouse hovers over the 3 scenario buttons]**

> "We're looking at a pharma environment — SCADA historians, MES systems, LIMS databases. All containing GxP-regulated data. I have three attack scenarios here. Let's trigger the worst one — a LockBit 4.0 ransomware attack on the SCADA historian."

**Direction:** Move mouse slowly across the three scenario cards as you describe them. Pause on the red Ransomware button.

---

### SCENE 3 — TRIGGER & SNOWFLAKE DETECTION (0:22–0:42)

**[ON SCREEN: Dashboard — CLICK the Ransomware button]**

> "I click — and immediately, Snowflake's AI anomaly detection kicks in. It's scanning hundreds of network events and endpoint telemetry in real time..."

**[Step 1 goes RUNNING (amber pulse) then COMPLETE]**
**[Snowflake Detection panel slides in below the timeline]**

> "...and there it is. SCADA-HIST-01 — threat score 9.87 out of 10. The AI model detected C2 callbacks to a Russian IP, shadow copy deletion, lateral movement via SMB to two other hosts. This is a confirmed LockBit attack."

**Direction:** As the Snowflake panel appears, slowly mouse down to it. Point at the threat score bar for SCADA-HIST-01, then the other two hosts. Take your time here — this is the money shot.

---

### SCENE 4 — SERVICENOW TICKET (0:42–0:55)

**[ON SCREEN: Dashboard — Step 2 goes RUNNING then COMPLETE. Incident card fills in.]**

> "The workflow automatically creates a real ServiceNow incident — INC number, P1 Critical — with all the Snowflake detection data attached as a work note. No human had to type anything."

**Direction:** Point at the ServiceNow Incident card on the left showing the INC number and "LIVE" badge. If time allows, quickly switch to Tab 3 (ServiceNow) to flash the real ticket in the list, then switch back.

---

### SCENE 5 — DELL CYBER RECOVERY (0:55–1:20)

**[ON SCREEN: Dashboard — Steps 3-4-5 progress through. Air gap opens/closes, CyberSense runs.]**

> "Now Dell Cyber Recovery takes over. Watch the air gap — it opens, replicates the data into the isolated cyber vault, then locks down again."

**[Step 3 completes — vault shows LOCKED]**

> "CyberSense — Dell's ML engine — scans the vault copy. 99.99% confidence: corruption detected. Twelve encrypted files identified across four compromised servers."

**[Steps 4-5 complete — CyberSense Report panel appears]**

> "But here's the key — CyberSense also identified a clean point-in-time copy from before the attack. That's our recovery point."

**Direction:** During vault sync, point at the air gap animation (Production → Vault). When the CyberSense report appears, slowly highlight the confidence score, corrupted file count, and the clean PIT copy ID.

---

### SCENE 6 — RECOVERY & RESOLUTION (1:20–1:40)

**[ON SCREEN: Steps 6-7 complete. Recovery bar fills. Incident shows "Resolved".]**

> "Recovery initiates from the clean copy — 1,704 files restored. And the workflow closes the loop: the ServiceNow incident is automatically resolved with a full forensic report attached."

**Direction:** Watch the recovery progress bar fill to 100%. Point at the incident card when it flips to "Resolved" (green).

---

### SCENE 7 — THE PROOF (1:40–1:55)

**[ON SCREEN: Switch to Tab 3 — ServiceNow incident list]**

> "And if we jump into ServiceNow — here's the real ticket. Work notes from Snowflake's AI detection, Dell CyberSense forensics, and the full recovery report. Every step documented, every action auditable."

**Direction:** In ServiceNow, click on the incident to open it. Scroll down to the Work Notes section to show the Snowflake and CyberSense notes. Pause for 2-3 seconds so viewers can see it's real.

---

### SCENE 8 — CLOSE (1:55–2:05)

**[ON SCREEN: Switch back to Tab 1 — Dashboard showing everything complete, all green]**

> "From detection to full recovery in under two minutes. Automated. Auditable. Air-gapped. That's Dell Cyber Recovery for regulated industries."

**Direction:** End on the dashboard with all 7 steps green. Hold for 2 seconds, then stop recording.

---

## POST-PRODUCTION TIPS

### LinkedIn Post Text (suggestion)
```
What does automated cyber recovery look like for pharma?

→ Snowflake AI detects ransomware on SCADA systems
→ ServiceNow incident created automatically
→ Dell Cyber Recovery isolates, analyzes, and restores
→ Full forensic report — zero manual intervention

Everything you see here is live:
• Real Snowflake queries against SIEM telemetry
• Real ServiceNow tickets with work notes
• Dell CR vault sync, CyberSense ML analysis, point-in-time recovery

From detection to recovery in under 2 minutes.

#CyberRecovery #Dell #Pharma #Ransomware #CyberSecurity
```

### Video Editing Notes
- Add a subtle dark intro card (0.5s): "CYBER RECOVERY DEMO" in monospace
- No background music (keeps it serious/technical)
- If you fumble a line, just pause and restart that sentence — easy to cut
- Export as MP4, H.264, 1080x1080 square crop for LinkedIn feed
- Add captions/subtitles — 80% of LinkedIn videos are watched on mute

### Behind-the-Scenes Post (for later)
Save this for a follow-up post: "How I built this entire demo with Claude Code in one session" — show the architecture, the code, the real integrations. That's your AI/dev credibility post.

---

## REHEARSAL CHECKLIST

- [ ] Read the script aloud 2-3 times for timing
- [ ] Practice the tab switches (Dashboard → ServiceNow → back)
- [ ] Do one full dry run with recording
- [ ] Check that the demo takes ~30s (steps 1-7) — adjust browser position if needed
- [ ] Make sure ServiceNow session won't expire mid-recording (refresh login)
- [ ] Snowflake warehouse CYBER_WH is set to AUTO_RESUME=TRUE (it is)

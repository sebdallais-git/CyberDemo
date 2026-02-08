.PHONY: setup run run-live demo tunnel-help clean

setup:
	pip3 install -r requirements.txt

# Mock mode: start mock Dell CR server in background + main app
run:
	@echo "Starting mock Dell CR server on :14778..."
	@DELLCR_MODE=mock python3 -m mock_dellcr.server &
	@sleep 1
	@echo "Starting CyberDemo dashboard on :8888..."
	DELLCR_MODE=mock python3 -m app.main

# Live mode: main app only (tunnel + real ServiceNow must be configured)
run-live:
	@echo "Starting CyberDemo dashboard on :8888 (LIVE mode)..."
	DELLCR_MODE=live python3 -m app.main

# Trigger a demo scenario via API
demo:
	curl -s -X POST http://localhost:8888/api/scenario \
		-H "Content-Type: application/json" \
		-d '{"type":"ransomware"}' | python3 -m json.tool

# Print SSH tunnel instructions
tunnel-help:
	@echo ""
	@echo "=== Dell HOL Tunnel Setup ==="
	@echo ""
	@echo "From inside the Dell HOL-0408-01 VM, run:"
	@echo "  ssh -R 14778:<CR_MGMT_IP>:14778 user@<YOUR_MAC_IP>"
	@echo ""
	@echo "Or use bore.pub (no SSH needed):"
	@echo "  bore local 14778 --to bore.pub"
	@echo ""
	@echo "Then set DELLCR_MODE=live in .env and run: make run-live"
	@echo ""

# Kill background processes
clean:
	@echo "Stopping background servers..."
	-@pkill -f "mock_dellcr.server" 2>/dev/null || true
	-@pkill -f "app.main" 2>/dev/null || true
	@echo "Done."

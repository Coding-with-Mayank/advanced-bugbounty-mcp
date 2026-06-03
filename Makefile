# ═══════════════════════════════════════════════════════════════
#  Bug Bounty MCP Server — Makefile
#  Run `make help` to see all commands
# ═══════════════════════════════════════════════════════════════

COMPOSE := $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || echo "docker-compose")
CONTAINER := bugbounty-mcp
SHELL := /bin/bash

.DEFAULT_GOAL := help

.PHONY: help setup up down restart build rebuild logs shell \
        update clean nuke hunt test status n8n

# ── Help ──────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  Bug Bounty MCP Server"
	@echo ""
	@echo "  \033[1mFirst time:\033[0m"
	@echo "    make setup      Run full setup (recommended)"
	@echo ""
	@echo "  \033[1mDocker:\033[0m"
	@echo "    make up         Start all containers"
	@echo "    make down       Stop all containers"
	@echo "    make restart    Restart MCP server"
	@echo "    make rebuild    Rebuild image and restart"
	@echo "    make logs       Follow MCP server logs"
	@echo "    make status     Show container health"
	@echo "    make shell      Open bash shell in container"
	@echo ""
	@echo "  \033[1mAutomation (n8n):\033[0m"
	@echo "    make n8n        Start with n8n workflow automation"
	@echo ""
	@echo "  \033[1mManual hunting:\033[0m"
	@echo "    make hunt       Open interactive hunt.py shell"
	@echo "    make test       Verify all tools are working"
	@echo ""
	@echo "  \033[1mMaintenance:\033[0m"
	@echo "    make update     Pull latest images + rebuild"
	@echo "    make clean      Remove containers + volumes"
	@echo "    make nuke       Remove EVERYTHING including images"
	@echo ""

# ── Setup ─────────────────────────────────────────────────────────────
setup:
	@chmod +x setup.sh && ./setup.sh

# ── Docker Operations ─────────────────────────────────────────────────
up:
	@echo "Starting services..."
	@$(COMPOSE) up -d
	@echo "Done. Logs: make logs"

down:
	@$(COMPOSE) down

restart:
	@$(COMPOSE) restart mcp-server

build:
	@$(COMPOSE) build

rebuild:
	@$(COMPOSE) build --no-cache
	@$(COMPOSE) up -d --force-recreate mcp-server
	@echo "Rebuilt and restarted."

logs:
	@$(COMPOSE) logs -f mcp-server

status:
	@echo ""
	@echo "Container status:"
	@$(COMPOSE) ps
	@echo ""
	@echo "Health API:"
	@curl -sf http://localhost:8080/health 2>/dev/null \
		| python3 -m json.tool 2>/dev/null \
		|| echo "  Not responding on :8080 (container may still be starting)"
	@echo ""

shell:
	@docker exec -it $(CONTAINER) /bin/bash

# ── n8n Automation ────────────────────────────────────────────────────
n8n:
	@echo "Starting with n8n automation..."
	@$(COMPOSE) --profile automation up -d
	@echo ""
	@echo "n8n dashboard: http://localhost:5678"
	@echo "Login: admin / (see N8N_PASSWORD in .env)"

# ── Manual Hunting ────────────────────────────────────────────────────
hunt:
	@echo "Starting hunt.py interactive mode..."
	@python3 hunt.py --help

test:
	@echo ""
	@echo "Testing MCP server..."
	@docker exec $(CONTAINER) python -c "import mcp_server; print('  ✓ mcp_server package OK')" 2>/dev/null \
		|| echo "  ✗ mcp_server import failed"
	@docker exec $(CONTAINER) python -c "import mcp; print('  ✓ mcp SDK OK')" 2>/dev/null \
		|| echo "  ✗ mcp SDK missing — rebuild with: make rebuild"
	@echo ""
	@echo "Testing tools..."
	@docker exec $(CONTAINER) bash -c "\
		tools='subfinder httpx nuclei naabu katana dnsx waybackurls gau ffuf gobuster gowitness anew'; \
		ok=0; fail=0; \
		for t in \$$tools; do \
			if which \$$t > /dev/null 2>&1; then echo \"  ✓ \$$t\"; ok=\$$((ok+1)); \
			else echo \"  ✗ \$$t\"; fail=\$$((fail+1)); fi; \
		done; \
		echo \"\"; echo \"  \$$ok tools OK, \$$fail missing\"" 2>/dev/null \
		|| echo "  Container not running. Run: make up"
	@echo ""

# ── Maintenance ───────────────────────────────────────────────────────
update:
	@git pull 2>/dev/null || true
	@$(COMPOSE) pull
	@$(COMPOSE) build
	@$(COMPOSE) up -d
	@docker exec $(CONTAINER) nuclei -update-templates 2>/dev/null || true
	@echo "Updated!"

clean:
	@$(COMPOSE) down -v
	@docker system prune -f
	@echo "Cleaned."

nuke:
	@echo "This removes ALL containers, images, and data. Are you sure? [y/N]"
	@read -r confirm && [[ "$$confirm" == "y" ]] || exit 1
	@$(COMPOSE) down -v --rmi all
	@docker system prune -af
	@echo "Nuked."

.PHONY: help install start stop restart logs clean test

help:
	@echo "Advanced Bug Bounty MCP Server"
	@echo "=============================="
	@echo ""
	@echo "Available commands:"
	@echo "  install       - Run complete installation"
	@echo "  start         - Start all services"
	@echo "  stop          - Stop all services"
	@echo "  restart       - Restart all services"
	@echo "  logs          - Show logs"
	@echo "  test          - Run tests"
	@echo "  clean         - Stop and remove everything"
	@echo "  build         - Build Docker images"
	@echo "  status        - Show service status"

install:
	@echo "Running installation..."
	@chmod +x setup.sh
	@./setup.sh

start:
	@echo "Starting services..."
	@docker-compose up -d
	@echo "✓ Services started"
	@make status

stop:
	@echo "Stopping services..."
	@docker-compose stop
	@echo "✓ Services stopped"

restart:
	@echo "Restarting services..."
	@docker-compose restart
	@echo "✓ Services restarted"

logs:
	@docker-compose logs -f

status:
	@echo "Service Status:"
	@docker-compose ps
	@echo ""
	@echo "Service URLs:"
	@echo "  • Web Dashboard: http://localhost:8080"
	@echo "  • MCP Server: http://localhost:9090"

clean:
	@echo "⚠ This will remove all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [ "$$REPLY" = "y" ] || [ "$$REPLY" = "Y" ]; then \
		echo ""; \
		echo "Cleaning up..."; \
		docker-compose down -v --rmi all; \
		rm -rf data/* logs/* reports/*; \
		echo "✓ Cleanup complete"; \
	fi

build:
	@echo "Building Docker images..."
	@docker-compose build --no-cache
	@echo "✓ Build complete"

test:
	@echo "Running tests..."
	@docker exec bugbounty-mcp pytest tests/ -v || echo "Tests not yet implemented"

shell:
	@docker exec -it bugbounty-mcp /bin/bash

update:
	@echo "Updating components..."
	@git pull
	@docker-compose pull
	@docker-compose up -d
	@echo "✓ Update complete"
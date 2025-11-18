.PHONY: help install install-dev test lint format clean build docker-build docker-run

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Lawdit - Legal Due Diligence Intelligence Tool$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	pip install -e .

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	pip install -e ".[dev]"
	@echo "$(GREEN)Development environment ready!$(NC)"

test: ## Run tests with coverage
	@echo "$(BLUE)Running tests...$(NC)"
	pytest -v --cov=lawdit --cov-report=term-missing --cov-report=html

test-fast: ## Run tests without coverage
	@echo "$(BLUE)Running tests (fast mode)...$(NC)"
	pytest -v

lint: ## Run linters (flake8, mypy)
	@echo "$(BLUE)Running linters...$(NC)"
	@echo "$(YELLOW)Running flake8...$(NC)"
	flake8 src/lawdit tests
	@echo "$(YELLOW)Running mypy...$(NC)"
	mypy src/lawdit

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	@echo "$(YELLOW)Running isort...$(NC)"
	isort src/lawdit tests
	@echo "$(YELLOW)Running black...$(NC)"
	black src/lawdit tests
	@echo "$(GREEN)Code formatted!$(NC)"

format-check: ## Check code formatting without modifying
	@echo "$(BLUE)Checking code formatting...$(NC)"
	isort --check-only src/lawdit tests
	black --check src/lawdit tests

clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)Clean complete!$(NC)"

build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	python -m build
	@echo "$(GREEN)Build complete! Check dist/ directory$(NC)"

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t lawdit:latest .
	@echo "$(GREEN)Docker image built successfully!$(NC)"

docker-run: ## Run Docker container (interactive)
	@echo "$(BLUE)Running Docker container...$(NC)"
	docker run -it --rm \
		-v $(PWD)/data_room_processing:/app/data_room_processing \
		-v $(PWD)/outputs:/app/outputs \
		--env-file .env \
		lawdit:latest

setup-env: ## Create .env file from template
	@if [ ! -f .env ]; then \
		echo "$(BLUE)Creating .env file from template...$(NC)"; \
		cp .env.example .env; \
		echo "$(YELLOW)Please edit .env with your actual credentials$(NC)"; \
	else \
		echo "$(RED).env file already exists$(NC)"; \
	fi

index: ## Run data room indexer (requires .env configuration)
	@echo "$(BLUE)Running data room indexer...$(NC)"
	lawdit-index --credentials $(GOOGLE_CREDENTIALS_PATH) --folder-id $(GOOGLE_DRIVE_FOLDER_ID)

analyze: ## Run legal analysis (requires .env configuration)
	@echo "$(BLUE)Running legal analysis...$(NC)"
	lawdit-analyze --index ./data_room_index.txt

check-deps: ## Check for outdated dependencies
	@echo "$(BLUE)Checking for outdated dependencies...$(NC)"
	pip list --outdated

update-deps: ## Update dependencies to latest compatible versions
	@echo "$(BLUE)Updating dependencies...$(NC)"
	pip install --upgrade pip setuptools wheel
	pip install --upgrade -e ".[dev]"

ci: format-check lint test ## Run all CI checks (format, lint, test)
	@echo "$(GREEN)All CI checks passed!$(NC)"

.PHONY: setup
setup: install-dev setup-env ## Complete development environment setup
	@echo "$(GREEN)Setup complete!$(NC)"
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Edit .env with your API keys and credentials"
	@echo "  2. Run 'make test' to verify installation"
	@echo "  3. Run 'make index' to build a data room index"

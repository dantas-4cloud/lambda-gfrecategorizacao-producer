.PHONY: help install test lint format clean deploy terraform

help:
	@echo "Lambda Recategorización - Comandos disponibles"
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install dependencies"
	@echo "  make install-dev      - Install dev dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run unit tests"
	@echo "  make test-coverage    - Run tests with coverage"
	@echo "  make test-watch       - Run tests in watch mode"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             - Run linting checks"
	@echo "  make format           - Format code with black"
	@echo "  make type-check       - Run type checking"
	@echo "  make quality          - Run all quality checks"
	@echo ""
	@echo "Terraform:"
	@echo "  make terraform-init   - Initialize terraform"
	@echo "  make terraform-plan   - Plan infrastructure (env=ENV required)"
	@echo "  make terraform-apply  - Apply infrastructure (env=ENV required)"
	@echo ""
	@echo "Build:"
	@echo "  make build            - Build lambda zip"
	@echo "  make package          - Package for lambda"
	@echo ""
	@echo "Local Development:"
	@echo "  make local-invoke     - Invoke lambda locally"
	@echo "  make clean            - Clean build artifacts"
	@echo ""

install:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

install-dev: install
	. venv/bin/activate && pip install pytest-watch pytest-xdist pytest-html

test:
	pytest tests/ -v

test-coverage:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

test-watch:
	ptw tests/ -- -v

lint:
	ruff check src/ tests/

format:
	black src/ tests/

type-check:
	mypy src/ --ignore-missing-imports

quality: lint type-check test-coverage
	@echo "All quality checks passed!"

terraform-init:
	cd terraform && terraform init

terraform-plan:
	@if [ -z "$(env)" ]; then echo "Please specify env=dev/hom/prod"; exit 1; fi
	cd terraform && terraform plan -var-file="environments/$(env).tfvars" -out=$(env).tfplan

terraform-apply:
	@if [ -z "$(env)" ]; then echo "Please specify env=dev/hom/prod"; exit 1; fi
	cd terraform && terraform apply $(env).tfplan

terraform-destroy:
	@if [ -z "$(env)" ]; then echo "Please specify env=dev/hom/prod"; exit 1; fi
	cd terraform && terraform destroy -var-file="environments/$(env).tfvars"

build:
	rm -f lambda_function.zip
	cd src && zip -r ../lambda_function.zip . -x "*.pyc" "__pycache__/*"

package: build
	@echo "Lambda package created at lambda_function.zip"

local-invoke:
	sam local invoke recategorizationProducer \
		--event tests/fixtures/mock_events.py \
		--env-vars terraform/environments/dev.tfvars

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .tox htmlcov .coverage dist build
	rm -f lambda_function.zip

all: clean quality test build
	@echo "Build complete!"

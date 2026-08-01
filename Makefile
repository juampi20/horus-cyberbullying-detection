.DEFAULT_GOAL := help

.PHONY: help init_env lint format check test types

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

init_env: ## Create .venv with uv (Python 3.11) and install requirements
	uv venv .venv --python 3.11
	uv pip install -r requirements.txt

lint: ## Lint with ruff (E, F, I, UP, B, S)
	uvx ruff check --config .code_quality/ruff.toml src_fastapi src_streamlit

format: ## Auto-format with ruff
	uvx ruff format --config .code_quality/ruff.toml src_fastapi src_streamlit

check: lint ## Lint + verify formatting
	uvx ruff format --check --config .code_quality/ruff.toml src_fastapi src_streamlit

types: ## Static type check with mypy
	uvx mypy --config-file .code_quality/mypy.ini src_fastapi src_streamlit

test: ## Run tests (placeholder - no tests configured yet)
	@echo "No tests configured yet."

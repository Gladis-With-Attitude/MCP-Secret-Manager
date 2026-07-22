from __future__ import annotations

import os

os.environ.setdefault("MCP_SECRET_MANAGER_ENVIRONMENT", "test")
os.environ.setdefault("MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_EMAIL", "admin@example.test")
os.environ.setdefault("MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_NAME", "Test Administrator")

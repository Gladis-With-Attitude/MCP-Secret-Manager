# MCP Secret Manager

MCP Secret Manager is an open source, self-hosted secret manager for AI-first and
MCP-native infrastructure.

The official source of truth lives in `docs/`. Implementation work must follow
the architecture, security model, testing strategy and accepted ADRs documented
there.

## Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
make install-dev
make up
make verify
```

The local PostgreSQL service is configured through `configs/local.env.example`.
Values in that file are development placeholders only and must not be used for
production.

"""replace plaintext secret versions with encrypted envelope fields

Revision ID: 0005_encrypt_secret_versions
Revises: 0004_create_secret_versions
Create Date: 2026-07-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0005_encrypt_secret_versions"
down_revision = "0004_create_secret_versions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM secret_versions) THEN
                RAISE EXCEPTION
                    'Cannot migrate plaintext secret_versions automatically; '
                    'export or recreate existing rows before applying encrypted storage.';
            END IF;
        END $$;
        """
    )
    op.drop_constraint(
        "ck_secret_versions_value_required",
        "secret_versions",
        type_="check",
    )
    op.drop_column("secret_versions", "value")
    op.add_column(
        "secret_versions",
        sa.Column("encrypted_value", sa.LargeBinary(), nullable=False),
    )
    op.add_column(
        "secret_versions",
        sa.Column("encrypted_dek", sa.LargeBinary(), nullable=False),
    )
    op.add_column(
        "secret_versions",
        sa.Column("nonce", sa.LargeBinary(), nullable=False),
    )
    op.add_column(
        "secret_versions",
        sa.Column("authentication_tag", sa.LargeBinary(), nullable=False),
    )
    op.add_column(
        "secret_versions",
        sa.Column("encryption_algorithm", sa.String(length=64), nullable=False),
    )
    op.add_column(
        "secret_versions",
        sa.Column("key_version", sa.Integer(), nullable=False),
    )
    op.create_check_constraint(
        "ck_secret_versions_encrypted_value_required",
        "secret_versions",
        "octet_length(encrypted_value) >= 1",
    )
    op.create_check_constraint(
        "ck_secret_versions_encrypted_dek_required",
        "secret_versions",
        "octet_length(encrypted_dek) >= 1",
    )
    op.create_check_constraint(
        "ck_secret_versions_nonce_aes_gcm_size",
        "secret_versions",
        "octet_length(nonce) = 12",
    )
    op.create_check_constraint(
        "ck_secret_versions_authentication_tag_aes_gcm_size",
        "secret_versions",
        "octet_length(authentication_tag) = 16",
    )
    op.create_check_constraint(
        "ck_secret_versions_encryption_algorithm_required",
        "secret_versions",
        "char_length(encryption_algorithm) >= 1",
    )
    op.create_check_constraint(
        "ck_secret_versions_key_version_positive",
        "secret_versions",
        "key_version >= 1",
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM secret_versions) THEN
                RAISE EXCEPTION
                    'Cannot downgrade encrypted secret_versions to plaintext storage.';
            END IF;
        END $$;
        """
    )
    op.drop_constraint(
        "ck_secret_versions_key_version_positive",
        "secret_versions",
        type_="check",
    )
    op.drop_constraint(
        "ck_secret_versions_encryption_algorithm_required",
        "secret_versions",
        type_="check",
    )
    op.drop_constraint(
        "ck_secret_versions_authentication_tag_aes_gcm_size",
        "secret_versions",
        type_="check",
    )
    op.drop_constraint(
        "ck_secret_versions_nonce_aes_gcm_size",
        "secret_versions",
        type_="check",
    )
    op.drop_constraint(
        "ck_secret_versions_encrypted_dek_required",
        "secret_versions",
        type_="check",
    )
    op.drop_constraint(
        "ck_secret_versions_encrypted_value_required",
        "secret_versions",
        type_="check",
    )
    op.drop_column("secret_versions", "key_version")
    op.drop_column("secret_versions", "encryption_algorithm")
    op.drop_column("secret_versions", "authentication_tag")
    op.drop_column("secret_versions", "nonce")
    op.drop_column("secret_versions", "encrypted_dek")
    op.drop_column("secret_versions", "encrypted_value")
    op.add_column("secret_versions", sa.Column("value", sa.Text(), nullable=False))
    op.create_check_constraint(
        "ck_secret_versions_value_required",
        "secret_versions",
        "char_length(value) >= 1",
    )

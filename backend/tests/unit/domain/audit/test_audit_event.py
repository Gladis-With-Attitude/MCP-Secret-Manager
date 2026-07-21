from __future__ import annotations

from uuid import UUID

import pytest

from domain.audit.entities import AuditEvent
from domain.audit.exceptions import AuditValueError
from domain.audit.value_objects import (
    AuditAction,
    AuditActorType,
    AuditEventId,
    AuditResourceType,
    AuditResult,
)


def test_audit_event_id_can_be_created_from_string() -> None:
    event_id = AuditEventId.from_string("b40fc39f-dbc9-4d7e-907d-d2ef0ca58d44")

    assert event_id.value == UUID("b40fc39f-dbc9-4d7e-907d-d2ef0ca58d44")
    assert str(event_id) == "b40fc39f-dbc9-4d7e-907d-d2ef0ca58d44"


def test_audit_event_normalizes_optional_fields() -> None:
    event = AuditEvent.create(
        actor_id=" ",
        actor_type=AuditActorType("User"),
        action=AuditAction(" Vault.Create "),
        resource_type=AuditResourceType(" Vault "),
        resource_id=" ",
        result=AuditResult.SUCCESS,
        ip_address=" 127.0.0.1 ",
        user_agent=" test-client ",
        request_id=" req-1 ",
        metadata={"name": "Production"},
    )

    assert event.actor_id is None
    assert event.actor_type.value == "user"
    assert event.action.value == "vault.create"
    assert event.resource_type.value == "vault"
    assert event.resource_id is None
    assert event.ip_address == "127.0.0.1"
    assert event.user_agent == "test-client"
    assert event.request_id == "req-1"


def test_audit_value_objects_reject_invalid_names() -> None:
    with pytest.raises(AuditValueError):
        AuditAction("secret read")
    with pytest.raises(AuditValueError):
        AuditActorType("")
    with pytest.raises(AuditValueError):
        AuditResourceType("a" * 65)


def test_audit_event_equality_is_based_on_id() -> None:
    event = AuditEvent.create(
        actor_id="user-1",
        actor_type=AuditActorType("user"),
        action=AuditAction("secret.read"),
        resource_type=AuditResourceType("secret"),
        resource_id="secret-1",
        result=AuditResult.SUCCESS,
        ip_address=None,
        user_agent=None,
        request_id=None,
    )
    same_event = AuditEvent(
        id=event.id,
        timestamp=event.timestamp,
        actor_id="user-2",
        actor_type=AuditActorType("service_account"),
        action=AuditAction("secret.decrypt"),
        resource_type=AuditResourceType("secret"),
        resource_id="secret-2",
        result=AuditResult.FAILURE,
        ip_address=None,
        user_agent=None,
        request_id=None,
        metadata={},
    )

    assert event == same_event
    assert hash(event) == hash(same_event)

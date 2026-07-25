import type { QueryParams } from "@/lib/api";

import type { AuditEventDto, AuditListParamsDto, AuditListResponseDto } from "../api/audit-dto";
import type {
  AuditEvent,
  AuditFilterFormValues,
  AuditFilters,
  AuditList,
  AuditResult,
} from "../types/audit";
import { AUDIT_DEFAULT_LIMIT, AUDIT_MAX_LIMIT } from "../validation/audit-schema";

function normalizeAuditResult(result?: string | null): AuditResult {
  if (result?.toUpperCase() === "SUCCESS" || result?.toLowerCase() === "success") {
    return "success";
  }

  if (result?.toUpperCase() === "FAILURE" || result?.toLowerCase() === "failure") {
    return "failure";
  }

  return "unknown";
}

function sanitizeAuditMetadata(metadata?: AuditEventDto["metadata"]): AuditEvent["metadata"] {
  const safeMetadata = metadata ?? {};
  const sensitivePattern = /(secret|token|api[_-]?key|password|value|credential)/i;

  return Object.fromEntries(
    Object.entries(safeMetadata).filter(([key]) => !sensitivePattern.test(key)),
  );
}

function mapAuditEventDtoToAuditEvent(dto: AuditEventDto): AuditEvent {
  return {
    action: dto.action,
    actorId: dto.actor_id,
    actorType: dto.actor_type,
    id: dto.id,
    ipAddress: dto.ip_address,
    metadata: sanitizeAuditMetadata(dto.metadata),
    requestId: dto.request_id,
    resourceId: dto.resource_id,
    resourceType: dto.resource_type,
    result: normalizeAuditResult(dto.result),
    timestamp: dto.timestamp,
    userAgent: dto.user_agent,
  };
}

function getAuditListItems(dto: AuditListResponseDto): AuditEventDto[] {
  if (Array.isArray(dto)) {
    return dto;
  }

  return dto.data;
}

function mapAuditListResponseToAuditList(
  dto: AuditListResponseDto,
  filters: AuditFilters = {},
): AuditList {
  const events = getAuditListItems(dto).map(mapAuditEventDtoToAuditEvent);
  const limit = normalizeAuditLimit(filters.limit);
  const offset = Math.max(0, filters.offset ?? 0);

  return {
    events,
    pagination: {
      hasNextPage: events.length >= limit,
      hasPreviousPage: offset > 0,
      limit,
      offset,
    },
  };
}

function normalizeAuditLimit(limit?: number): number {
  if (!limit) {
    return AUDIT_DEFAULT_LIMIT;
  }

  return Math.min(AUDIT_MAX_LIMIT, Math.max(1, limit));
}

function mapAuditFiltersToParams(filters: AuditFilters = {}): AuditListParamsDto & QueryParams {
  return {
    action: filters.action?.trim() || undefined,
    actor_id: filters.actorId?.trim() || undefined,
    end_date: filters.endDate || undefined,
    limit: normalizeAuditLimit(filters.limit),
    offset: Math.max(0, filters.offset ?? 0),
    q: filters.query?.trim() || undefined,
    resource_id: filters.resourceId?.trim() || undefined,
    resource_type: filters.resourceType?.trim() || undefined,
    result: filters.result && filters.result !== "all" ? filters.result.toUpperCase() : undefined,
    start_date: filters.startDate || undefined,
  };
}

function mapAuditFilterFormToFilters(
  values: AuditFilterFormValues,
  previous: AuditFilters = {},
): AuditFilters {
  return {
    action: values.action?.trim() || undefined,
    actorId: values.actorId?.trim() || undefined,
    endDate: values.endDate || undefined,
    limit: normalizeAuditLimit(previous.limit),
    offset: 0,
    query: values.query?.trim() || undefined,
    resourceId: values.resourceId?.trim() || undefined,
    resourceType: values.resourceType?.trim() || undefined,
    result: values.result,
    startDate: values.startDate || undefined,
  };
}

function auditEventMatchesQuery(event: AuditEvent, query?: string): boolean {
  const normalizedQuery = query?.trim().toLowerCase();

  if (!normalizedQuery) {
    return true;
  }

  return JSON.stringify(event).toLowerCase().includes(normalizedQuery);
}

export {
  auditEventMatchesQuery,
  mapAuditEventDtoToAuditEvent,
  mapAuditFilterFormToFilters,
  mapAuditFiltersToParams,
  mapAuditListResponseToAuditList,
  normalizeAuditLimit,
  normalizeAuditResult,
  sanitizeAuditMetadata,
};

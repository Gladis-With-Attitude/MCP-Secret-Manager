import { ApiNotFoundError, get } from "@/lib/api";

import { auditEventMatchesQuery, mapAuditEventDtoToAuditEvent } from "../mappers/audit-mappers";
import type { AuditEvent } from "../types/audit";
import type { AuditListParamsDto, AuditListResponseDto } from "./audit-dto";

async function listAuditEvents(params?: AuditListParamsDto): Promise<AuditListResponseDto> {
  return get<AuditListResponseDto>("/v1/audit", { params });
}

async function getAuditEvent(eventId: string): Promise<AuditEvent> {
  const response = await listAuditEvents({ limit: 500, offset: 0, q: eventId, search: eventId });
  const items = Array.isArray(response) ? response : response.data;
  const event = items.map(mapAuditEventDtoToAuditEvent).find((item) => item.id === eventId);

  if (!event || !auditEventMatchesQuery(event, eventId)) {
    throw new ApiNotFoundError({ message: "Audit event not found." });
  }

  return event;
}

const auditService = {
  getAuditEvent,
  listAuditEvents,
};

export { auditService, getAuditEvent, listAuditEvents };

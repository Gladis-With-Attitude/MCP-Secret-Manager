import { get } from "@/lib/api";

import { mapAuditEventDtoToAuditEvent } from "../mappers/audit-mappers";
import type { AuditEvent } from "../types/audit";
import type { AuditEventDto, AuditListParamsDto, AuditListResponseDto } from "./audit-dto";

async function listAuditEvents(params?: AuditListParamsDto): Promise<AuditListResponseDto> {
  return get<AuditListResponseDto>("/v1/audit/events", { params });
}

async function getAuditEvent(eventId: string): Promise<AuditEvent> {
  return mapAuditEventDtoToAuditEvent(await get<AuditEventDto>(`/v1/audit/events/${eventId}`));
}

const auditService = {
  getAuditEvent,
  listAuditEvents,
};

export { auditService, getAuditEvent, listAuditEvents };

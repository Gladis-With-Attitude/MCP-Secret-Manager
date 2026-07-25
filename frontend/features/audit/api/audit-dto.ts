import type { PaginatedResponse, SuccessResponse } from "@/lib/api";

import type { AuditMetadata } from "../types/audit";

type AuditEventDto = {
  action: string;
  actor_id?: string | null;
  actor_type: string;
  id: string;
  ip_address?: string | null;
  metadata?: AuditMetadata | null;
  request_id?: string | null;
  resource_id?: string | null;
  resource_type: string;
  result: string;
  timestamp: string;
  user_agent?: string | null;
};

type AuditListEnvelopeDto = PaginatedResponse<AuditEventDto>;
type AuditListResponseDto =
  AuditEventDto[] | AuditListEnvelopeDto | SuccessResponse<AuditEventDto[]>;

type AuditListParamsDto = {
  action?: string;
  actor_id?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
  q?: string;
  resource_id?: string;
  resource_type?: string;
  result?: string;
  start_date?: string;
};

export type { AuditEventDto, AuditListParamsDto, AuditListResponseDto };

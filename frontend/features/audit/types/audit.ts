type AuditResult = "failure" | "success" | "unknown";
type AuditFilterResult = Exclude<AuditResult, "unknown"> | "all";

type AuditMetadata = Record<string, boolean | number | string | null>;

type AuditEvent = {
  action: string;
  actorId?: string | null;
  actorType: string;
  id: string;
  ipAddress?: string | null;
  metadata: AuditMetadata;
  requestId?: string | null;
  resourceId?: string | null;
  resourceType: string;
  result: AuditResult;
  timestamp: string;
  userAgent?: string | null;
};

type AuditFilters = {
  action?: string;
  actorId?: string;
  endDate?: string;
  limit?: number;
  offset?: number;
  query?: string;
  resourceId?: string;
  resourceType?: string;
  result?: AuditFilterResult;
  startDate?: string;
};

type AuditList = {
  events: AuditEvent[];
  pagination: {
    hasNextPage: boolean;
    hasPreviousPage: boolean;
    limit: number;
    offset: number;
  };
};

type AuditFilterFormValues = {
  action?: string;
  actorId?: string;
  endDate?: string;
  query?: string;
  resourceId?: string;
  resourceType?: string;
  result: AuditFilterResult;
  startDate?: string;
};

export type {
  AuditEvent,
  AuditFilterFormValues,
  AuditFilterResult,
  AuditFilters,
  AuditList,
  AuditMetadata,
  AuditResult,
};

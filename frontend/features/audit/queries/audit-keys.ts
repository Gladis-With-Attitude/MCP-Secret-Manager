import type { AuditFilters } from "../types/audit";

const auditQueryKeys = {
  all: ["audit"] as const,
  detail: (eventId: string) => [...auditQueryKeys.details(), eventId] as const,
  details: () => [...auditQueryKeys.all, "detail"] as const,
  list: (filters: AuditFilters = {}) => [...auditQueryKeys.lists(), filters] as const,
  lists: () => [...auditQueryKeys.all, "list"] as const,
};

export { auditQueryKeys };

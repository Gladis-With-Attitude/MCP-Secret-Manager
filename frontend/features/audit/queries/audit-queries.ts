import { useQuery } from "@tanstack/react-query";

import { getAuditEvent, listAuditEvents } from "../api/audit-service";
import { mapAuditFiltersToParams, mapAuditListResponseToAuditList } from "../mappers/audit-mappers";
import type { AuditFilters } from "../types/audit";
import { auditQueryKeys } from "./audit-keys";

function useAuditListQuery(filters: AuditFilters = {}) {
  return useQuery({
    queryFn: async () =>
      mapAuditListResponseToAuditList(
        await listAuditEvents(mapAuditFiltersToParams(filters)),
        filters,
      ),
    queryKey: auditQueryKeys.list(filters),
  });
}

function useAuditDetailQuery(eventId: string) {
  return useQuery({
    enabled: Boolean(eventId),
    queryFn: async () => getAuditEvent(eventId),
    queryKey: auditQueryKeys.detail(eventId),
    retry: false,
  });
}

export { useAuditDetailQuery, useAuditListQuery };

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AuditDetails } from "@/features/audit";

describe("AuditDetails", () => {
  it("renders event detail metadata only", () => {
    render(
      <AuditDetails
        event={{
          action: "secret.read",
          actorId: "actor_1",
          actorType: "user",
          id: "event_1",
          metadata: { reason: "allowed" },
          requestId: "request_1",
          resourceId: "secret_1",
          resourceType: "secret",
          result: "success",
          timestamp: "2026-01-01T00:00:00Z",
        }}
      />,
    );

    expect(screen.getByText("event_1")).toBeInTheDocument();
    expect(screen.getByText("reason")).toBeInTheDocument();
    expect(screen.queryByText(/secret-value/i)).not.toBeInTheDocument();
  });
});

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AuditTable } from "@/features/audit";

describe("AuditTable", () => {
  it("renders large audit result sets without exposing sensitive metadata", () => {
    const events = Array.from({ length: 250 }, (_, index) => ({
      action: "secret.read",
      actorId: `actor_${index}`,
      actorType: "user",
      id: `event_${index}`,
      metadata: {},
      resourceId: `secret_${index}`,
      resourceType: "secret",
      result: "success" as const,
      timestamp: "2026-01-01T00:00:00Z",
    }));

    render(<AuditTable events={events} />);

    expect(screen.getByText("actor_0")).toBeInTheDocument();
    expect(screen.getAllByText("secret.read")).toHaveLength(250);
    expect(screen.queryByText(/token/i)).not.toBeInTheDocument();
  });
});

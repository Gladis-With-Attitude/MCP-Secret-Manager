import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SecretVersionTimeline } from "@/features/secret-version";

describe("SecretVersionTimeline", () => {
  it("renders metadata-only version history", () => {
    render(
      <SecretVersionTimeline
        versions={[
          {
            createdAt: "2026-01-01T00:00:00Z",
            id: "version_2",
            isCurrent: true,
            metadata: {},
            permissions: {},
            secretId: "secret_1",
            status: "current",
            version: 2,
          },
        ]}
      />,
    );

    expect(screen.getByLabelText("Secret version timeline")).toBeInTheDocument();
    expect(screen.getByText("Current version 2")).toBeInTheDocument();
    expect(screen.queryByText(/secret-value/i)).not.toBeInTheDocument();
  });
});

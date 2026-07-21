import { describe, expect, it } from "vitest";

import {
  PROJECT_DESCRIPTION_MAX_LENGTH,
  PROJECT_NAME_MAX_LENGTH,
  PROJECT_NAME_MIN_LENGTH,
  projectFormSchema,
} from "@/features/project/validation/project-schema";

describe("project validation", () => {
  it("accepts a valid project form payload", () => {
    expect(projectFormSchema.safeParse({ description: "", name: "API" }).success).toBe(true);
  });

  it("enforces backend project name length constraints", () => {
    expect(
      projectFormSchema.safeParse({ name: "a".repeat(PROJECT_NAME_MIN_LENGTH - 1) }).success,
    ).toBe(false);
    expect(
      projectFormSchema.safeParse({ name: "a".repeat(PROJECT_NAME_MAX_LENGTH + 1) }).success,
    ).toBe(false);
  });

  it("keeps descriptions non-sensitive and bounded", () => {
    expect(
      projectFormSchema.safeParse({
        description: "a".repeat(PROJECT_DESCRIPTION_MAX_LENGTH + 1),
        name: "API",
      }).success,
    ).toBe(false);
  });
});

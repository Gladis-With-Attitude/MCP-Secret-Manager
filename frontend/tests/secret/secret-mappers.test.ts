import { describe, expect, it } from "vitest";

import {
  canUseSecretAction,
  mapSecretDtoToSecret,
  mapSecretFiltersToParams,
  mapSecretFormToCreateDto,
  mapSecretListResponseToSecretList,
  mapSecretSchemaValuesToFormValues,
} from "@/features/secret/mappers/secret-mappers";

describe("secret mappers", () => {
  it("maps backend secret metadata without value material", () => {
    const secret = mapSecretDtoToSecret({
      current_version: 3,
      description: "Database credential",
      id: "secret_1",
      key: "DATABASE_PASSWORD",
      metadata: { owner: "platform" },
      permissions: { read_value: false, update: true },
      project_id: "project_1",
      tags: ["production"],
      type: "password",
      vault_id: "vault_1",
    });

    expect(secret).toMatchObject({
      currentVersion: 3,
      metadata: { owner: "platform" },
      name: "DATABASE_PASSWORD",
      permissions: { readValue: false, update: true },
      projectId: "project_1",
      tags: ["production"],
      type: "password",
      vaultId: "vault_1",
    });
    expect(JSON.stringify(secret)).not.toContain("value");
  });

  it("maps project-scoped list envelopes", () => {
    const result = mapSecretListResponseToSecretList(
      {
        data: [{ id: "secret_1", key: "API_TOKEN", project_id: "project_1" }],
        pagination: { page: 1, pageSize: 20, total: 1 },
        permissions: { create: true },
        success: true,
      },
      "project_1",
    );

    expect(result.projectId).toBe("project_1");
    expect(result.items[0]?.projectId).toBe("project_1");
    expect(result.permissions.create).toBe(true);
  });

  it("serializes search filters and form payloads", () => {
    expect(
      mapSecretFiltersToParams({ page: 2, search: " api ", status: "active", type: "token" }),
    ).toEqual({
      archived: undefined,
      page: 2,
      page_size: undefined,
      provider: undefined,
      q: "api",
      search: "api",
      status: "active",
      type: "token",
    });

    expect(
      mapSecretFormToCreateDto({
        description: " notes ",
        metadata: { owner: "platform" },
        name: "API_TOKEN",
        tags: ["production"],
        type: "token",
        value: "sensitive-value",
      }),
    ).toEqual({
      description: "notes",
      key: "API_TOKEN",
      metadata: { owner: "platform" },
      tags: ["production"],
      type: "token",
      value: "sensitive-value",
    });
  });

  it("maps form schema fields into typed form values", () => {
    expect(
      mapSecretSchemaValuesToFormValues({
        metadataJson: '{"owner":"platform","rotated":false}',
        name: "API_TOKEN",
        tagsInput: "production, api",
        type: "api_key",
        value: "secret",
      }),
    ).toEqual({
      description: undefined,
      metadata: { owner: "platform", rotated: false },
      name: "API_TOKEN",
      tags: ["production", "api"],
      type: "api_key",
      value: "secret",
    });
  });

  it("hides an action only when backend permission explicitly denies it", () => {
    expect(canUseSecretAction({}, "readValue")).toBe(true);
    expect(canUseSecretAction({ readValue: false }, "readValue")).toBe(false);
  });
});

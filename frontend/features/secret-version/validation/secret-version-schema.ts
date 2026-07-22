import { z } from "zod";

const SECRET_VERSION_VALUE_MAX_LENGTH = 65536;
const SECRET_VERSION_NOTE_MAX_LENGTH = 280;
const SECRET_VERSION_METADATA_MAX_LENGTH = 2000;

function parseSecretVersionMetadata(
  rawMetadata: string,
): Record<string, boolean | number | string> {
  const trimmed = rawMetadata.trim();

  if (!trimmed) {
    return {};
  }

  const parsed: unknown = JSON.parse(trimmed);

  if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") {
    throw new Error("Metadata must be a JSON object.");
  }

  return Object.fromEntries(
    Object.entries(parsed).map(([key, value]) => {
      if (typeof value !== "boolean" && typeof value !== "number" && typeof value !== "string") {
        throw new Error("Metadata values must be strings, numbers or booleans.");
      }

      return [key, value];
    }),
  );
}

const secretVersionMetadataJsonSchema = z
  .string()
  .trim()
  .max(
    SECRET_VERSION_METADATA_MAX_LENGTH,
    `Metadata must contain at most ${SECRET_VERSION_METADATA_MAX_LENGTH} characters.`,
  )
  .refine((value) => {
    try {
      parseSecretVersionMetadata(value);
      return true;
    } catch {
      return false;
    }
  }, "Metadata must be a JSON object with string, number or boolean values.");

const secretVersionRotateFormSchema = z.object({
  makeCurrent: z.boolean(),
  metadataJson: secretVersionMetadataJsonSchema,
  note: z
    .string()
    .trim()
    .max(
      SECRET_VERSION_NOTE_MAX_LENGTH,
      `Note must contain at most ${SECRET_VERSION_NOTE_MAX_LENGTH} characters.`,
    )
    .optional()
    .or(z.literal("")),
  value: z
    .string()
    .min(1, "New secret value is required.")
    .max(
      SECRET_VERSION_VALUE_MAX_LENGTH,
      `Secret value must contain at most ${SECRET_VERSION_VALUE_MAX_LENGTH} characters.`,
    ),
});

const secretVersionRestoreFormSchema = z.object({
  reason: z
    .string()
    .trim()
    .max(
      SECRET_VERSION_NOTE_MAX_LENGTH,
      `Reason must contain at most ${SECRET_VERSION_NOTE_MAX_LENGTH} characters.`,
    )
    .optional()
    .or(z.literal("")),
  versionId: z.string().min(1, "Version id is required."),
});

type SecretVersionRotateSchemaValues = z.infer<typeof secretVersionRotateFormSchema>;
type SecretVersionRestoreSchemaValues = z.infer<typeof secretVersionRestoreFormSchema>;

export {
  parseSecretVersionMetadata,
  SECRET_VERSION_METADATA_MAX_LENGTH,
  SECRET_VERSION_NOTE_MAX_LENGTH,
  SECRET_VERSION_VALUE_MAX_LENGTH,
  secretVersionRestoreFormSchema,
  secretVersionRotateFormSchema,
};
export type { SecretVersionRestoreSchemaValues, SecretVersionRotateSchemaValues };

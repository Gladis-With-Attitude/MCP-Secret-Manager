import { z } from "zod";

const SECRET_NAME_MIN_LENGTH = 3;
const SECRET_NAME_MAX_LENGTH = 128;
const SECRET_DESCRIPTION_MAX_LENGTH = 280;
const SECRET_VALUE_MAX_LENGTH = 65536;
const SECRET_TAG_MAX_LENGTH = 40;
const SECRET_TAGS_MAX_COUNT = 12;
const SECRET_METADATA_MAX_LENGTH = 2000;
const SECRET_NAME_PATTERN = /^[A-Z0-9_]+$/;
const SECRET_TAG_PATTERN = /^[a-zA-Z0-9_.:-]+$/;

const secretTypeOptions = [
  "api_key",
  "certificate",
  "generic",
  "password",
  "token",
  "other",
] as const;

function parseSecretTags(rawTags: string): string[] {
  return rawTags
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

function parseSecretMetadata(rawMetadata: string): Record<string, boolean | number | string> {
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

const secretMetadataJsonSchema = z
  .string()
  .trim()
  .max(
    SECRET_METADATA_MAX_LENGTH,
    `Metadata must contain at most ${SECRET_METADATA_MAX_LENGTH} characters.`,
  )
  .refine((value) => {
    try {
      parseSecretMetadata(value);
      return true;
    } catch {
      return false;
    }
  }, "Metadata must be a JSON object with string, number or boolean values.");

const secretTagsInputSchema = z
  .string()
  .refine((value) => parseSecretTags(value).length <= SECRET_TAGS_MAX_COUNT, {
    message: `Use at most ${SECRET_TAGS_MAX_COUNT} tags.`,
  })
  .refine((value) => parseSecretTags(value).every((tag) => tag.length <= SECRET_TAG_MAX_LENGTH), {
    message: `Each tag must contain at most ${SECRET_TAG_MAX_LENGTH} characters.`,
  })
  .refine((value) => parseSecretTags(value).every((tag) => SECRET_TAG_PATTERN.test(tag)), {
    message: "Tags may contain letters, numbers, underscore, dot, colon or dash.",
  });

const secretMetadataFormSchema = z.object({
  description: z
    .string()
    .trim()
    .max(
      SECRET_DESCRIPTION_MAX_LENGTH,
      `Description must contain at most ${SECRET_DESCRIPTION_MAX_LENGTH} characters.`,
    )
    .optional()
    .or(z.literal("")),
  metadataJson: secretMetadataJsonSchema,
  name: z
    .string()
    .trim()
    .min(
      SECRET_NAME_MIN_LENGTH,
      `Secret name must contain at least ${SECRET_NAME_MIN_LENGTH} characters.`,
    )
    .max(
      SECRET_NAME_MAX_LENGTH,
      `Secret name must contain at most ${SECRET_NAME_MAX_LENGTH} characters.`,
    )
    .regex(
      SECRET_NAME_PATTERN,
      "Secret name must contain only A-Z, 0-9 and underscore characters.",
    ),
  tagsInput: secretTagsInputSchema,
  type: z.enum(secretTypeOptions),
});

const secretCreateFormSchema = secretMetadataFormSchema.extend({
  value: z
    .string()
    .min(1, "Initial secret value is required.")
    .max(
      SECRET_VALUE_MAX_LENGTH,
      `Secret value must contain at most ${SECRET_VALUE_MAX_LENGTH} characters.`,
    ),
});

type SecretMetadataFormSchemaValues = z.infer<typeof secretMetadataFormSchema>;
type SecretCreateFormSchemaValues = z.infer<typeof secretCreateFormSchema>;

export {
  parseSecretMetadata,
  parseSecretTags,
  SECRET_DESCRIPTION_MAX_LENGTH,
  SECRET_METADATA_MAX_LENGTH,
  SECRET_NAME_MAX_LENGTH,
  SECRET_NAME_MIN_LENGTH,
  SECRET_NAME_PATTERN,
  SECRET_TAGS_MAX_COUNT,
  SECRET_VALUE_MAX_LENGTH,
  secretCreateFormSchema,
  secretMetadataFormSchema,
  secretTypeOptions,
};
export type { SecretCreateFormSchemaValues, SecretMetadataFormSchemaValues };

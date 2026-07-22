import { z } from "zod";

const API_KEY_NAME_MIN_LENGTH = 3;
const API_KEY_NAME_MAX_LENGTH = 80;
const API_KEY_DESCRIPTION_MAX_LENGTH = 280;
const API_KEY_OWNER_ID_MAX_LENGTH = 128;
const API_KEY_ITEM_MAX_LENGTH = 80;
const API_KEY_ITEMS_MAX_COUNT = 24;
const API_KEY_NAME_PATTERN = /^[A-Za-z0-9_.:-]+$/;
const API_KEY_ITEM_PATTERN = /^[A-Za-z0-9_.:-]+$/;

const apiKeyOwnerTypeOptions = ["service_account", "user"] as const;

function parseApiKeyItems(rawItems: string): string[] {
  return rawItems
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

const apiKeyCsvSchema = z
  .string()
  .refine((value) => parseApiKeyItems(value).length <= API_KEY_ITEMS_MAX_COUNT, {
    message: `Use at most ${API_KEY_ITEMS_MAX_COUNT} entries.`,
  })
  .refine(
    (value) => parseApiKeyItems(value).every((item) => item.length <= API_KEY_ITEM_MAX_LENGTH),
    {
      message: `Each entry must contain at most ${API_KEY_ITEM_MAX_LENGTH} characters.`,
    },
  )
  .refine((value) => parseApiKeyItems(value).every((item) => API_KEY_ITEM_PATTERN.test(item)), {
    message: "Entries may contain letters, numbers, underscore, dot, colon or dash.",
  });

const apiKeyFormSchema = z.object({
  description: z
    .string()
    .trim()
    .max(
      API_KEY_DESCRIPTION_MAX_LENGTH,
      `Description must contain at most ${API_KEY_DESCRIPTION_MAX_LENGTH} characters.`,
    )
    .optional()
    .or(z.literal("")),
  expiresAt: z
    .string()
    .refine((value) => {
      if (!value) {
        return true;
      }

      return !Number.isNaN(Date.parse(value));
    }, "Expiration must be a valid date.")
    .optional()
    .or(z.literal("")),
  name: z
    .string()
    .trim()
    .min(
      API_KEY_NAME_MIN_LENGTH,
      `API key name must contain at least ${API_KEY_NAME_MIN_LENGTH} characters.`,
    )
    .max(
      API_KEY_NAME_MAX_LENGTH,
      `API key name must contain at most ${API_KEY_NAME_MAX_LENGTH} characters.`,
    )
    .regex(
      API_KEY_NAME_PATTERN,
      "API key name may contain letters, numbers, underscore, dot, colon or dash.",
    ),
  ownerId: z
    .string()
    .trim()
    .min(1, "Owner id is required.")
    .max(
      API_KEY_OWNER_ID_MAX_LENGTH,
      `Owner id must contain at most ${API_KEY_OWNER_ID_MAX_LENGTH} characters.`,
    ),
  ownerType: z.enum(apiKeyOwnerTypeOptions),
  permissionsInput: apiKeyCsvSchema.refine((value) => parseApiKeyItems(value).length > 0, {
    message: "At least one permission is required.",
  }),
  scopesInput: apiKeyCsvSchema.refine((value) => parseApiKeyItems(value).length > 0, {
    message: "At least one scope is required.",
  }),
});

type ApiKeyFormSchemaValues = z.infer<typeof apiKeyFormSchema>;

export {
  API_KEY_DESCRIPTION_MAX_LENGTH,
  API_KEY_ITEM_MAX_LENGTH,
  API_KEY_ITEMS_MAX_COUNT,
  API_KEY_NAME_MAX_LENGTH,
  API_KEY_NAME_MIN_LENGTH,
  apiKeyFormSchema,
  apiKeyOwnerTypeOptions,
  parseApiKeyItems,
};
export type { ApiKeyFormSchemaValues };

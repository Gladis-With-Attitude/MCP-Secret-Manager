import { z } from "zod";

const VAULT_NAME_MIN_LENGTH = 3;
const VAULT_NAME_MAX_LENGTH = 100;
const VAULT_DESCRIPTION_MAX_LENGTH = 280;

const vaultFormSchema = z.object({
  description: z
    .string()
    .trim()
    .max(
      VAULT_DESCRIPTION_MAX_LENGTH,
      `Description must contain at most ${VAULT_DESCRIPTION_MAX_LENGTH} characters.`,
    )
    .optional()
    .or(z.literal("")),
  name: z
    .string()
    .trim()
    .min(
      VAULT_NAME_MIN_LENGTH,
      `Vault name must contain at least ${VAULT_NAME_MIN_LENGTH} characters.`,
    )
    .max(
      VAULT_NAME_MAX_LENGTH,
      `Vault name must contain at most ${VAULT_NAME_MAX_LENGTH} characters.`,
    ),
});

type VaultFormSchemaValues = z.infer<typeof vaultFormSchema>;

export {
  VAULT_DESCRIPTION_MAX_LENGTH,
  VAULT_NAME_MAX_LENGTH,
  VAULT_NAME_MIN_LENGTH,
  vaultFormSchema,
};
export type { VaultFormSchemaValues };

import { Text } from "@/components/typography/text";

type ApiKeyExpirationProps = {
  expiresAt?: string | null;
};

function ApiKeyExpiration({ expiresAt }: ApiKeyExpirationProps) {
  if (!expiresAt) {
    return <Text size="sm">No expiration</Text>;
  }

  return <Text size="sm">{expiresAt}</Text>;
}

export { ApiKeyExpiration };
export type { ApiKeyExpirationProps };

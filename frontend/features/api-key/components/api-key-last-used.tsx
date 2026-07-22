import { Text } from "@/components/typography/text";

type ApiKeyLastUsedProps = {
  lastUsedAt?: string | null;
};

function ApiKeyLastUsed({ lastUsedAt }: ApiKeyLastUsedProps) {
  return (
    <Text className={!lastUsedAt ? "text-muted-foreground" : undefined} size="sm">
      {lastUsedAt ?? "Never used"}
    </Text>
  );
}

export { ApiKeyLastUsed };
export type { ApiKeyLastUsedProps };

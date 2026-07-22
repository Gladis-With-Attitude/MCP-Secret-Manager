import { Badge } from "@/components/display/badge";

import type { SecretType } from "../types/secret";

type SecretTypeBadgeProps = {
  type: SecretType;
};

const typeLabel = {
  api_key: "API key",
  certificate: "Certificate",
  generic: "Generic",
  other: "Other",
  password: "Password",
  token: "Token",
} satisfies Record<SecretType, string>;

function SecretTypeBadge({ type }: SecretTypeBadgeProps) {
  return <Badge variant="info">{typeLabel[type]}</Badge>;
}

export { SecretTypeBadge, typeLabel };
export type { SecretTypeBadgeProps };

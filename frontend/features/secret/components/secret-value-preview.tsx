"use client";

import { useEffect, useState } from "react";

import { usePathname } from "next/navigation";

import { Copy, Eye, EyeOff } from "lucide-react";

import { Button } from "@/components/buttons/button";
import { Card } from "@/components/display/card";
import { ErrorState } from "@/components/feedback/error-state";
import { Stack } from "@/components/layout/stack";
import { Text } from "@/components/typography/text";
import { isApiError } from "@/lib/api";

import type { SecretValueResult } from "../types/secret";

type SecretValuePreviewProps = {
  canReveal?: boolean;
  onReveal: () => Promise<SecretValueResult>;
};

function SecretValuePreview({ canReveal = true, onReveal }: SecretValuePreviewProps) {
  const pathname = usePathname();
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isRevealed, setIsRevealed] = useState(false);
  const [isRevealing, setIsRevealing] = useState(false);
  const [secretValue, setSecretValue] = useState<string | null>(null);

  const clearSecretValue = () => {
    setCopied(false);
    setError(null);
    setIsRevealed(false);
    setSecretValue(null);
  };

  useEffect(() => clearSecretValue, [pathname]);

  const handleReveal = async () => {
    setCopied(false);
    setError(null);
    setIsRevealing(true);

    try {
      const result = await onReveal();
      setSecretValue(result.value);
      setIsRevealed(true);
    } catch (caughtError) {
      setSecretValue(null);
      setIsRevealed(false);
      setError(
        isApiError(caughtError) ? caughtError.userMessage : "Unable to reveal secret value.",
      );
    } finally {
      setIsRevealing(false);
    }
  };

  const handleCopy = async () => {
    if (!secretValue) {
      return;
    }

    try {
      await navigator.clipboard.writeText(secretValue);
      setCopied(true);
    } catch {
      setCopied(false);
      setError("Unable to copy secret value.");
    }
  };

  return (
    <Card variant="security">
      <Stack>
        <div>
          <h2 className="text-base font-semibold text-foreground">Secret value</h2>
          <Text tone="muted">
            Values are masked by default. Reveal is explicit, temporary and may be audited.
          </Text>
        </div>
        {error ? <ErrorState description={error} title="Value access failed" /> : null}
        <div className="rounded-md border border-border bg-muted/30 p-4">
          {isRevealed && secretValue ? (
            <code className="block max-h-48 overflow-auto break-all text-sm text-foreground">
              {secretValue}
            </code>
          ) : (
            <span
              className="text-sm tracking-widest text-muted-foreground"
              aria-label="Masked secret value"
            >
              ••••••••••••••••
            </span>
          )}
        </div>
        <div className="flex flex-wrap justify-end gap-2">
          {isRevealed ? (
            <>
              <Button onClick={handleCopy} variant="outline">
                <Copy aria-hidden="true" className="size-4" />
                {copied ? "Copied" : "Copy value"}
              </Button>
              <Button onClick={clearSecretValue} variant="outline">
                <EyeOff aria-hidden="true" className="size-4" />
                Hide
              </Button>
            </>
          ) : (
            <Button
              disabled={!canReveal}
              isLoading={isRevealing}
              onClick={handleReveal}
              variant="danger"
            >
              <Eye aria-hidden="true" className="size-4" />
              Reveal value
            </Button>
          )}
        </div>
      </Stack>
    </Card>
  );
}

export { SecretValuePreview };
export type { SecretValuePreviewProps };

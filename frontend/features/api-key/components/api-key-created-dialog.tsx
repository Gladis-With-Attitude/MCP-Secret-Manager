"use client";

import { useState } from "react";

import { Copy } from "lucide-react";

import { Button } from "@/components/buttons/button";
import { Card } from "@/components/display/card";
import { Dialog } from "@/components/overlay/dialog";
import { Text } from "@/components/typography/text";

import type { ApiKeyCreated } from "../types/api-key";

type ApiKeyCreatedDialogProps = {
  createdApiKey: ApiKeyCreated | null;
  onClose: () => void;
};

function ApiKeyCreatedDialog({ createdApiKey, onClose }: ApiKeyCreatedDialogProps) {
  const [copyState, setCopyState] = useState<"copied" | "failed" | "idle">("idle");
  const apiKeyValue = createdApiKey?.apiKeyValue;

  async function handleCopy() {
    if (!apiKeyValue) {
      return;
    }

    try {
      await navigator.clipboard.writeText(apiKeyValue);
      setCopyState("copied");
    } catch {
      setCopyState("failed");
    }
  }

  function handleOpenChange(open: boolean) {
    if (!open) {
      setCopyState("idle");
      onClose();
    }
  }

  return (
    <Dialog
      description="Copy this API key now. The full value is shown only once and cannot be retrieved later."
      onOpenChange={handleOpenChange}
      open={Boolean(createdApiKey)}
      title="API key created"
    >
      <div className="grid gap-4">
        <Card variant="security">
          <Text className="mb-2 font-medium">One-time value</Text>
          {apiKeyValue ? (
            <code className="block max-h-40 overflow-auto break-all rounded-md bg-muted p-3 text-sm text-foreground">
              {apiKeyValue}
            </code>
          ) : (
            <Text className="text-muted-foreground" size="sm">
              The backend did not return a full API key value.
            </Text>
          )}
        </Card>
        <Text className="text-muted-foreground" size="sm">
          Closing this dialog immediately clears the value from React state.
        </Text>
        <div className="flex flex-wrap justify-end gap-2">
          <Button disabled={!apiKeyValue} onClick={handleCopy} variant="outline">
            <Copy aria-hidden="true" className="size-4" />
            {copyState === "copied" ? "Copied" : "Copy"}
          </Button>
          <Button onClick={() => handleOpenChange(false)}>I have saved it</Button>
        </div>
        {copyState === "failed" ? (
          <p className="text-sm text-destructive" role="alert">
            Copy failed. Select and copy the value manually before closing.
          </p>
        ) : null}
      </div>
    </Dialog>
  );
}

export { ApiKeyCreatedDialog };
export type { ApiKeyCreatedDialogProps };

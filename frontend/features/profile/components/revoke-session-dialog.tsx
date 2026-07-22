"use client";

import { Button } from "@/components/buttons/button";
import { Dialog } from "@/components/overlay/dialog";

import type { ActiveSession } from "../types/profile";

type RevokeSessionDialogProps = {
  isOpen: boolean;
  isSubmitting?: boolean;
  onConfirm: () => void;
  onOpenChange: (open: boolean) => void;
  session: ActiveSession | null;
};

function RevokeSessionDialog({
  isOpen,
  isSubmitting = false,
  onConfirm,
  onOpenChange,
  session,
}: RevokeSessionDialogProps) {
  return (
    <Dialog
      description="This revokes a session according to backend session policy."
      footer={
        <>
          <Button disabled={isSubmitting} onClick={() => onOpenChange(false)} variant="outline">
            Cancel
          </Button>
          <Button disabled={!session} isLoading={isSubmitting} onClick={onConfirm} variant="danger">
            Revoke session
          </Button>
        </>
      }
      onOpenChange={onOpenChange}
      open={isOpen}
      title="Revoke session"
    >
      <p className="text-sm text-muted-foreground">
        {session
          ? `Revoke ${session.device ?? "this session"}. Current sessions cannot be revoked here.`
          : "No session selected."}
      </p>
    </Dialog>
  );
}

export { RevokeSessionDialog };
export type { RevokeSessionDialogProps };

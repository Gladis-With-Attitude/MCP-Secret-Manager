"use client";

import { Button } from "@/components/buttons/button";
import { Dialog } from "@/components/overlay/dialog";

import type { UserRole } from "../types/rbac";

type RemoveRoleDialogProps = {
  isOpen: boolean;
  isSubmitting?: boolean;
  onConfirm: () => void;
  onOpenChange: (open: boolean) => void;
  userRole: UserRole | null;
};

function RemoveRoleDialog({
  isOpen,
  isSubmitting = false,
  onConfirm,
  onOpenChange,
  userRole,
}: RemoveRoleDialogProps) {
  return (
    <Dialog
      description="This revokes an actor role assignment. The backend validates the operation and audit trail."
      footer={
        <>
          <Button disabled={isSubmitting} onClick={() => onOpenChange(false)} variant="outline">
            Cancel
          </Button>
          <Button
            disabled={!userRole}
            isLoading={isSubmitting}
            onClick={onConfirm}
            variant="danger"
          >
            Revoke assignment
          </Button>
        </>
      }
      onOpenChange={onOpenChange}
      open={isOpen}
      title="Revoke role assignment"
    >
      <p className="text-sm text-muted-foreground">
        {userRole
          ? `Revoke ${userRole.roleName} from actor ${userRole.actorId}.`
          : "No assignment selected."}
      </p>
    </Dialog>
  );
}

export { RemoveRoleDialog };
export type { RemoveRoleDialogProps };

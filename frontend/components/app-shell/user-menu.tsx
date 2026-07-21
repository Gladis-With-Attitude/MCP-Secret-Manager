"use client";

import { LogOut, UserCircle } from "lucide-react";

import { Button } from "@/components/buttons/button";
import { useAuth } from "@/hooks/use-auth";

function UserMenu() {
  const auth = useAuth();
  const label = auth.user?.name ?? auth.user?.email ?? "Session";

  return (
    <div className="flex items-center gap-2">
      <div className="hidden min-w-0 text-right sm:block">
        <p className="truncate text-sm font-medium text-foreground">{label}</p>
        <p className="truncate text-xs text-muted-foreground">{auth.status}</p>
      </div>
      <Button onClick={() => void auth.logout()} size="compact" variant="ghost">
        <UserCircle aria-hidden="true" className="size-4" />
        <span className="hidden sm:inline">Account</span>
        <LogOut aria-hidden="true" className="size-4" />
      </Button>
    </div>
  );
}

export { UserMenu };

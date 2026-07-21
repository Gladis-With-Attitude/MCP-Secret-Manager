import { Bell } from "lucide-react";

import { IconButton } from "@/components/buttons/icon-button";

function NotificationCenter() {
  return (
    <IconButton
      aria-disabled="true"
      icon={<Bell className="size-4" />}
      label="Notifications"
      variant="ghost"
    />
  );
}

export { NotificationCenter };

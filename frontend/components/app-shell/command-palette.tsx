import { Command } from "lucide-react";

import { Button } from "@/components/buttons/button";

function CommandPalette() {
  return (
    <Button aria-disabled="true" size="compact" variant="ghost">
      <Command aria-hidden="true" className="size-4" />
      <span className="hidden sm:inline">Command</span>
    </Button>
  );
}

export { CommandPalette };

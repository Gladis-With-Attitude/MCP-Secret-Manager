import { Search } from "lucide-react";

import { Button } from "@/components/buttons/button";

function GlobalSearch() {
  return (
    <Button
      aria-disabled="true"
      className="w-full justify-start text-muted-foreground sm:w-56"
      size="compact"
      variant="outline"
    >
      <Search aria-hidden="true" className="size-4" />
      <span>Search</span>
    </Button>
  );
}

export { GlobalSearch };

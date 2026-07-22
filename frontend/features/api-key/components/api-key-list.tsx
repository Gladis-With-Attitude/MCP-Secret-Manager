import { Grid } from "@/components/layout/grid";

import type { ApiKey } from "../types/api-key";
import { ApiKeyCard } from "./api-key-card";
import { ApiKeyTable } from "./api-key-table";

type ApiKeyListProps = {
  apiKeys: ApiKey[];
  canCreate?: boolean;
  canRevoke?: boolean;
  isFiltered?: boolean;
  onCreateAction?: React.ReactNode;
  onResetFilters?: () => void;
  onRevoke?: (apiKey: ApiKey) => void;
};

function ApiKeyList({
  apiKeys,
  canCreate,
  canRevoke,
  isFiltered,
  onCreateAction,
  onResetFilters,
  onRevoke,
}: ApiKeyListProps) {
  return (
    <>
      <div className="hidden md:block">
        <ApiKeyTable
          apiKeys={apiKeys}
          canCreate={canCreate}
          canRevoke={canRevoke}
          isFiltered={isFiltered}
          onCreateAction={onCreateAction}
          onResetFilters={onResetFilters}
          onRevoke={onRevoke}
        />
      </div>
      <div className="md:hidden">
        {apiKeys.length ? (
          <Grid>
            {apiKeys.map((apiKey) => (
              <ApiKeyCard
                apiKey={apiKey}
                canRevoke={canRevoke}
                key={apiKey.id}
                onRevoke={onRevoke}
              />
            ))}
          </Grid>
        ) : (
          <ApiKeyTable
            apiKeys={apiKeys}
            canCreate={canCreate}
            isFiltered={isFiltered}
            onCreateAction={onCreateAction}
            onResetFilters={onResetFilters}
          />
        )}
      </div>
    </>
  );
}

export { ApiKeyList };
export type { ApiKeyListProps };

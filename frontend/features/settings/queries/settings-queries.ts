import { useQuery } from "@tanstack/react-query";

import { getSettings } from "../api/settings-service";
import { mapSettingsResponseToSettingsState } from "../mappers/settings-mappers";
import { settingsQueryKeys } from "./settings-keys";

function useSettingsQuery() {
  return useQuery({
    queryFn: async () => mapSettingsResponseToSettingsState(await getSettings()),
    queryKey: settingsQueryKeys.settings(),
    retry: false,
  });
}

export { useSettingsQuery };

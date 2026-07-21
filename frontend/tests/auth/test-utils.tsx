import { QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactElement, ReactNode } from "react";

import { createQueryClient } from "@/lib/api/query-client";
import type { AuthProviderProps } from "@/providers";
import { AuthProvider } from "@/providers";

function renderWithAuth(ui: ReactElement, authProps: Partial<AuthProviderProps> = {}) {
  const queryClient = createQueryClient();

  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <AuthProvider initialize={false} {...authProps}>
          {children}
        </AuthProvider>
      </QueryClientProvider>
    );
  }

  return {
    queryClient,
    ...render(ui, { wrapper: Wrapper }),
  };
}

export { renderWithAuth };

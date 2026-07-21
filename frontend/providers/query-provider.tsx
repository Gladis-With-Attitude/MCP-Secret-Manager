"use client";

import { useState } from "react";

import { QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

import { createQueryClient } from "@/lib/api/query-client";

type QueryProviderProps = Readonly<{
  children: ReactNode;
}>;

export function QueryProvider({ children }: QueryProviderProps) {
  const [queryClient] = useState(createQueryClient);

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

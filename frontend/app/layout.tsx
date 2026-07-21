import type { Metadata } from "next";
import type { ReactNode } from "react";

import { QueryProvider, ThemeProvider } from "@/providers";

import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "MCP Secret Manager",
  description: "Frontend administration console for MCP Secret Manager.",
};

type RootLayoutProps = Readonly<{
  children: ReactNode;
}>;

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <QueryProvider>{children}</QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}

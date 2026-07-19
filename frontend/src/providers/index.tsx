"use client";

import * as React from "react";
import { ThemeProvider } from "./ThemeProvider";
import { QueryProvider } from "./QueryProvider";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <QueryProvider>
        {children}
      </QueryProvider>
    </ThemeProvider>
  );
}

"use client";

import { Loader2 } from "lucide-react";

interface LoadingUIProps {
  message?: string;
  variant?: "full" | "skeleton";
}

export function LoadingUI({ message = "Retrieving recommendations...", variant = "full" }: LoadingUIProps) {
  if (variant === "skeleton") {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full animate-pulse">
        {[1, 2, 3].map((idx) => (
          <div key={idx} className="h-44 rounded-xl border border-border bg-[#0b0c10]/40 p-5 space-y-4">
            <div className="h-6 w-1/3 rounded bg-muted" />
            <div className="space-y-2">
              <div className="h-4 w-full rounded bg-muted" />
              <div className="h-4 w-5/6 rounded bg-muted" />
            </div>
            <div className="h-8 w-24 rounded-full bg-muted" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[300px] w-full py-12">
      <div className="relative flex items-center justify-center">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <span className="absolute h-10 w-10 rounded-full border border-primary/20 animate-ping" />
      </div>
      <p className="mt-4 text-sm font-medium text-muted-foreground animate-pulse">
        {message}
      </p>
    </div>
  );
}

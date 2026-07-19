"use client";

import { AlertTriangle, RotateCcw } from "lucide-react";

interface ErrorUIProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorUI({ message = "Recommendation query failed.", onRetry }: ErrorUIProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[300px] w-full py-12 px-6 rounded-xl border border-red-500/20 bg-red-500/5 backdrop-blur-sm text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-500/10 text-red-400">
        <AlertTriangle className="h-6 w-6" />
      </div>
      
      <h3 className="mt-4 text-base font-semibold text-foreground">Recommendation Engine Error</h3>
      <p className="mt-2 text-sm text-muted-foreground max-w-md">
        {message}
      </p>

      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-6 flex items-center gap-2 px-5 py-2.5 rounded-full text-xs font-semibold text-primary border border-primary/20 bg-primary/10 hover:bg-primary/20 hover:border-primary transition-all duration-200 glow-btn cursor-pointer"
        >
          <RotateCcw className="h-4.5 w-4.5" />
          Retry Request
        </button>
      )}
    </div>
  );
}

"use client";

import Link from "next/link";
import { AlertCircle, Film } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center px-6">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 border border-primary/20 text-primary mb-6">
        <AlertCircle className="h-8 w-8" />
      </div>

      <h1 className="text-3xl font-extrabold tracking-tight">404 - Scene Not Found</h1>
      <p className="mt-3 text-sm text-muted-foreground max-w-sm leading-relaxed">
        The cinematic sequence you are looking for has been cut from the final reel, or is licensed in a different region.
      </p>

      <Link
        href="/"
        className="mt-8 flex items-center gap-2 px-6 py-3 rounded-full text-xs font-semibold bg-primary text-primary-foreground hover:opacity-90 transition-all glow-btn cursor-pointer"
      >
        <Film className="h-4 w-4" />
        Return to Feed
      </Link>
    </div>
  );
}

"use client";

import { Bookmark, Film } from "lucide-react";

export default function WatchlistPage() {
  return (
    <div className="space-y-6 max-w-4xl mx-auto py-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-bold tracking-tight">Your Watchlist</h1>
        <p className="text-sm text-muted-foreground">
          Movies bookmarked or recommended to watch next.
        </p>
      </div>

      <div className="flex flex-col items-center justify-center py-24 text-center rounded-xl border border-dashed border-border bg-[#0b0c10]/20 p-8">
        <Bookmark className="h-10 w-10 text-muted-foreground/60 mb-3" />
        <h3 className="font-semibold text-foreground text-sm">Watchlist is currently empty</h3>
        <p className="text-xs text-muted-foreground mt-1 max-w-xs leading-relaxed">
          Tap the bookmark badge on feed movies or ask the AI agent to bookmark films for you.
        </p>
      </div>
    </div>
  );
}

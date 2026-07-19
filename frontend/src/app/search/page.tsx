"use client";

import { Search, Sliders, Film } from "lucide-react";

export default function SearchPage() {
  return (
    <div className="space-y-8 max-w-4xl mx-auto py-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-bold tracking-tight">Semantic Query Search</h1>
        <p className="text-sm text-muted-foreground">
          Find movies by typing descriptors of plot details, moods, or themes.
        </p>
      </div>

      <div className="relative">
        <Search className="absolute top-1/2 left-4 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="e.g. A dystopian thriller where memories can be bought and sold..."
          className="w-full h-14 pl-12 pr-4 rounded-xl border border-border bg-[#0b0c10]/40 text-sm text-foreground focus:outline-none focus:border-primary transition-all duration-200"
          disabled
        />
      </div>

      <div className="rounded-xl border border-border bg-[#0b0c10]/20 p-6 space-y-4">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <Sliders className="h-4.5 w-4.5 text-primary" />
          Search filters
        </h3>
        
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div className="space-y-1.5">
            <label className="text-muted-foreground">Release Era</label>
            <select className="w-full h-9 rounded bg-[#06070a] border border-border px-2 text-muted-foreground" disabled>
              <option>All Eras</option>
            </select>
          </div>
          <div className="space-y-1.5">
            <label className="text-muted-foreground">Primary Genre</label>
            <select className="w-full h-9 rounded bg-[#06070a] border border-border px-2 text-muted-foreground" disabled>
              <option>All Genres</option>
            </select>
          </div>
          <div className="space-y-1.5">
            <label className="text-muted-foreground">Sort order</label>
            <select className="w-full h-9 rounded bg-[#06070a] border border-border px-2 text-muted-foreground" disabled>
              <option>Highest relevance match</option>
            </select>
          </div>
        </div>
      </div>

      <div className="flex flex-col items-center justify-center py-16 text-center text-muted-foreground">
        <Film className="h-10 w-10 text-muted-foreground/45 mb-3 animate-pulse" />
        <p className="text-xs">No search queries inputted yet.</p>
      </div>
    </div>
  );
}

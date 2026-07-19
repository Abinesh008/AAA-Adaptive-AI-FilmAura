"use client";

import { useSearch } from "@/hooks/useSearch";
import { MovieGrid } from "@/components/MovieGrid";
import { MovieGridSkeleton } from "@/components/LoadingSkeletons";
import { ErrorUI } from "@/components/ErrorUI";
import { Search, Sliders, Film } from "lucide-react";
import { useState } from "react";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [profile, setProfile] = useState("balanced");
  const [genreFilter, setGenreFilter] = useState("All");

  const { movies, answer, isLoading, isError, error, status, disambiguation } = useSearch(query, undefined, profile);

  const filteredMovies = genreFilter === "All" 
    ? movies 
    : movies.filter((m) => m.metadata?.genres?.includes(genreFilter));

  const genres = ["All", "Sci-Fi", "Action", "Drama", "Thriller", "Adventure"];

  return (
    <div className="space-y-8 max-w-7xl mx-auto py-6">
      
      {/* Search page header */}
      <div className="space-y-2">
        <h1 className="text-2xl font-bold tracking-tight">Semantic Movie Search</h1>
        <p className="text-sm text-muted-foreground">
          Enter plot motifs, atmospheric styles, or directors.
        </p>
      </div>

      {/* Input bar */}
      <div className="relative">
        <Search className="absolute top-1/2 left-4 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. A space thriller with black hole graphics and time dilation..."
          className="w-full h-14 pl-12 pr-4 rounded-xl border border-border bg-[#0b0c10]/40 text-sm text-foreground focus:outline-none focus:border-primary transition-all duration-200"
        />
      </div>

      {/* Advanced search controls */}
      <div className="rounded-xl border border-border bg-[#0b0c10]/20 p-6 space-y-4">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <Sliders className="h-4.5 w-4.5 text-primary" />
          Filter Settings
        </h3>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="space-y-1.5">
            <label className="text-muted-foreground">Retrieval Profile</label>
            <select 
              value={profile} 
              onChange={(e) => setProfile(e.target.value)}
              className="w-full h-10 rounded-xl bg-[#06070a] border border-border px-3 text-foreground focus:outline-none focus:border-primary transition-all"
            >
              <option value="fast">Fast search (Postgres only)</option>
              <option value="balanced">Balanced RAG (SQL + Vector)</option>
              <option value="quality">Quality search (SQL + Vector + KG Graph)</option>
            </select>
          </div>
          <div className="space-y-1.5">
            <label className="text-muted-foreground">Filter by Genre</label>
            <select 
              value={genreFilter} 
              onChange={(e) => setGenreFilter(e.target.value)}
              className="w-full h-10 rounded-xl bg-[#06070a] border border-border px-3 text-foreground focus:outline-none focus:border-primary transition-all"
            >
              {genres.map((g) => (
                <option key={g} value={g}>{g}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Disambiguation notices */}
      {status === "ambiguous" && disambiguation && (
        <div className="rounded-xl border border-secondary/20 bg-secondary/5 p-5 text-xs text-secondary-foreground space-y-3">
          <p className="font-semibold text-foreground">Clarification required:</p>
          <p className="text-muted-foreground">Your query matches multiple distinct parameters. Select one to re-run search:</p>
          <div className="flex flex-wrap gap-2.5">
            {disambiguation.candidates?.map((cand: any, idx: number) => (
              <button
                key={idx}
                onClick={() => setQuery(cand.title || cand)}
                className="px-3.5 py-1.5 rounded-lg border border-secondary/20 bg-secondary/10 hover:bg-secondary/20 text-[10px] text-secondary font-semibold transition-all cursor-pointer"
              >
                {cand.title || cand}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Results Section */}
      <div className="space-y-6">
        {isLoading ? (
          <MovieGridSkeleton count={4} />
        ) : isError ? (
          <ErrorUI message={error?.message || "Search retrieval loop failed. Verify API server."} />
        ) : query.trim().length <= 2 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center text-muted-foreground">
            <Film className="h-10 w-10 text-muted-foreground/35 mb-3" />
            <p className="text-xs">Type at least 3 characters to search semantic catalog.</p>
          </div>
        ) : filteredMovies.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center text-muted-foreground">
            <Film className="h-10 w-10 text-muted-foreground/35 mb-3 animate-pulse" />
            <p className="text-xs">No matching movies found in vectors or relational tables.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {answer && (
              <div className="p-4 rounded-xl border border-border bg-[#0b0c10]/40 text-xs leading-relaxed text-muted-foreground italic">
                <span className="font-bold text-foreground block not-italic mb-1.5">AI Insights:</span>
                &ldquo;{answer}&rdquo;
              </div>
            )}
            <MovieGrid movies={filteredMovies} />
          </div>
        )}
      </div>

    </div>
  );
}

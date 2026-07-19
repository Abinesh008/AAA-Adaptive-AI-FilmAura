"use client";

import { CandidateMovie } from "@/services/api";
import { Sparkles, ThumbsUp, ThumbsDown, Bookmark, ChevronRight } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

interface MovieCardProps {
  movie: CandidateMovie;
  onFeedback?: (movieId: number, type: "click" | "skip" | "bookmark" | "rating", val?: number) => void;
}

export function MovieCard({ movie, onFeedback }: MovieCardProps) {
  const [activeAction, setActiveAction] = useState<"like" | "dislike" | "bookmark" | null>(null);

  const handleAction = (type: "click" | "skip" | "bookmark") => {
    let stateMap: typeof activeAction = "like";
    if (type === "skip") stateMap = "dislike";
    if (type === "bookmark") stateMap = "bookmark";

    setActiveAction((prev) => (prev === stateMap ? null : stateMap));
    
    if (onFeedback) {
      onFeedback(movie.tmdb_id, type);
    }
  };

  const poster = movie.metadata?.poster_path || "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&auto=format&fit=crop&q=80";

  return (
    <div className="group relative flex flex-col justify-between overflow-hidden rounded-xl border border-border bg-[#0b0c10]/40 hover:border-primary/30 transition-all duration-300 hover:shadow-[0_0_15px_rgba(102,252,241,0.02)]">
      
      {/* Poster image area */}
      <div className="relative aspect-[16/10] w-full overflow-hidden bg-muted">
        <img
          src={poster}
          alt={movie.title}
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          loading="lazy"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#0b0c10] via-[#0b0c10]/20 to-transparent" />
        
        {/* Match Confidence Score tag */}
        <div className="absolute top-3 right-3 flex items-center gap-1 px-2.5 py-1 rounded-full border border-primary/20 bg-[#06070a]/80 text-[10px] font-bold text-primary backdrop-blur-sm shadow-[0_0_8px_rgba(102,252,241,0.2)]">
          <Sparkles className="h-3.5 w-3.5 animate-pulse text-primary" />
          {Math.round((movie.confidence || 0.85) * 100)}% Match
        </div>
      </div>

      {/* Details / Text area */}
      <div className="p-4 space-y-3 flex-1 flex flex-col justify-between">
        <div className="space-y-1.5">
          <div className="flex flex-wrap gap-1">
            {movie.metadata?.genres?.slice(0, 2).map((g) => (
              <span key={g} className="text-[8px] font-bold uppercase tracking-wider text-muted-foreground bg-muted/65 px-1.5 py-0.5 rounded">
                {g}
              </span>
            ))}
          </div>

          <h3 className="font-bold text-sm text-foreground group-hover:text-primary transition-colors line-clamp-1">
            {movie.title}
          </h3>
          
          <p className="text-[11px] text-muted-foreground line-clamp-2 leading-relaxed">
            {movie.metadata?.overview || "No plot description available in the registry context."}
          </p>
        </div>

        {/* Card Actions Panel */}
        <div className="flex items-center justify-between pt-3 border-t border-border/40 mt-4 text-[10px]">
          {/* Link detail trigger */}
          <Link
            href={`/movie/${movie.tmdb_id}`}
            className="flex items-center gap-1 text-muted-foreground hover:text-foreground font-semibold transition-colors"
          >
            Details
            <ChevronRight className="h-3 w-3" />
          </Link>

          {/* Interactive buttons */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => handleAction("click")}
              className={`p-1.5 rounded-full hover:bg-primary/10 hover:text-primary transition-colors cursor-pointer ${
                activeAction === "like" ? "text-primary bg-primary/10" : "text-muted-foreground"
              }`}
              title="Like"
            >
              <ThumbsUp className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => handleAction("skip")}
              className={`p-1.5 rounded-full hover:bg-red-500/10 hover:text-red-400 transition-colors cursor-pointer ${
                activeAction === "dislike" ? "text-red-400 bg-red-500/10" : "text-muted-foreground"
              }`}
              title="Dislike"
            >
              <ThumbsDown className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => handleAction("bookmark")}
              className={`p-1.5 rounded-full hover:bg-secondary/10 hover:text-secondary transition-colors cursor-pointer ${
                activeAction === "bookmark" ? "text-secondary bg-secondary/10" : "text-muted-foreground"
              }`}
              title="Save"
            >
              <Bookmark className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>
      
    </div>
  );
}

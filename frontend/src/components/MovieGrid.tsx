"use client";

import { CandidateMovie } from "@/services/api";
import { MovieCard } from "./MovieCard";

interface MovieGridProps {
  movies: CandidateMovie[];
  onFeedback?: (movieId: number, type: "click" | "skip" | "bookmark" | "rating", val?: number) => void;
}

export function MovieGrid({ movies, onFeedback }: MovieGridProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 w-full">
      {movies.map((movie, index) => (
        <MovieCard 
          key={`${movie.tmdb_id}-${index}`} 
          movie={movie} 
          onFeedback={onFeedback} 
        />
      ))}
    </div>
  );
}

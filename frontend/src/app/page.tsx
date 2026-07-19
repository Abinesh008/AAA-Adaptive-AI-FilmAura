"use client";

import { useRecommendations } from "@/hooks/useRecommendations";
import { useAuth } from "@/providers/AuthProvider";
import { LoadingUI } from "@/components/LoadingUI";
import { ErrorUI } from "@/components/ErrorUI";
import { 
  Sparkles, 
  ThumbsUp, 
  ThumbsDown, 
  Bookmark, 
  Tv, 
  Info,
  Layers
} from "lucide-react";
import { useState } from "react";

export default function Home() {
  const { user } = useAuth();
  const userId = user?.id || "guest_user";
  const { 
    recommendations, 
    experimentGroup, 
    isLoading, 
    isError, 
    error, 
    refetch, 
    submitFeedback, 
    userProfile 
  } = useRecommendations(userId, 6);

  const [ratedMovies, setRatedMovies] = useState<Record<number, "liked" | "disliked" | "bookmarked">>({});

  const handleRate = async (movieId: number, type: "click" | "skip" | "bookmark" | "rating", val?: number) => {
    try {
      await submitFeedback({ movieId, interactionType: type, rating: val });
      
      let mapping: "liked" | "disliked" | "bookmarked" = "liked";
      if (type === "skip") mapping = "disliked";
      if (type === "bookmark") mapping = "bookmarked";
      
      setRatedMovies((prev) => ({
        ...prev,
        [movieId]: mapping
      }));
    } catch (err) {
      console.error("Feedback mutation failed", err);
    }
  };

  return (
    <div className="space-y-8">
      
      {/* Dynamic Welcome Billboard */}
      <div className="relative rounded-2xl border border-border bg-[#0b0c10]/40 overflow-hidden p-6 md:p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-secondary/5 rounded-full blur-3xl pointer-events-none" />

        <div className="relative space-y-4">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-primary/20 bg-primary/5 text-xs text-primary">
            <Sparkles className="h-4 w-4" />
            Adaptive Intelligence Layer Active
          </div>
          
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight">
            Cinematic matches, <br className="sm:hidden" />
            <span className="bg-gradient-to-r from-primary via-cyan-400 to-secondary bg-clip-text text-transparent">
              tailored to your aura.
            </span>
          </h1>
          
          <p className="text-sm text-muted-foreground max-w-xl">
            Experience FilmAura's hybrid multi-objective recommendation engine. Our systems continuously balance relevance, novelty, freshness, and serendipity.
          </p>

          {/* Active AB experiment indicator */}
          <div className="flex flex-wrap gap-4 pt-2 text-xs">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border bg-[#06070a]/65 text-muted-foreground">
              <Layers className="h-4 w-4 text-primary" />
              Routing Variant: <span className="font-semibold text-foreground ml-1">{experimentGroup}</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border bg-[#06070a]/65 text-muted-foreground">
              <Info className="h-4 w-4 text-secondary" />
              Exploration Factor: <span className="font-semibold text-foreground ml-1">15% Breaker</span>
            </div>
          </div>
        </div>
      </div>

      {/* User Taste Coordinates Profile widget */}
      {userProfile && Object.keys(userProfile.genre_weights || {}).length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-bold tracking-wide">Your taste coordinates</h2>
          <div className="flex flex-wrap gap-3">
            {Object.entries(userProfile.genre_weights).map(([genre, weight]) => {
              // Convert HSL glow color dynamically based on weight affinity
              const affinity = Math.round(weight * 100);
              return (
                <div 
                  key={genre}
                  className="flex items-center gap-2 px-3.5 py-2 rounded-xl border border-border bg-[#0b0c10] text-xs transition-colors"
                >
                  <span className="font-semibold">{genre}</span>
                  <span className="text-[10px] text-primary bg-primary/10 px-1.5 py-0.5 rounded-full border border-primary/20">
                    {affinity > 0 ? `+${affinity}%` : `${affinity}%`}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Feed Recommendations Grid */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold tracking-wide">Personalized Feed</h2>
          <button 
            onClick={() => refetch()}
            className="text-xs text-primary hover:underline cursor-pointer"
          >
            Refresh recommendations
          </button>
        </div>

        {isLoading ? (
          <LoadingUI variant="skeleton" />
        ) : isError ? (
          <ErrorUI message={error?.message || "Verify your backend server at localhost:8000 is online."} onRetry={() => refetch()} />
        ) : recommendations.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 rounded-xl border border-dashed border-border bg-[#0b0c10]/20 text-center">
            <Tv className="h-10 w-10 text-muted-foreground mb-3" />
            <p className="text-sm text-muted-foreground">No recommendations generated.</p>
            <p className="text-xs text-muted-foreground/60 mt-1">Please seed movies in the admin tool or log watch actions.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recommendations.map((movie) => {
              const ratingState = ratedMovies[movie.movie_id];
              return (
                <div 
                  key={movie.movie_id}
                  className="group relative flex flex-col justify-between rounded-xl border border-border bg-[#0b0c10]/40 p-5 hover:border-primary/30 transition-all duration-300 hover:shadow-[0_0_15px_rgba(102,252,241,0.02)]"
                >
                  {/* Genre Tag Badge List */}
                  <div className="space-y-3">
                    <div className="flex flex-wrap gap-1.5">
                      {movie.genres.map((g) => (
                        <span 
                          key={g} 
                          className="text-[9px] font-bold uppercase tracking-wider text-muted-foreground bg-muted/65 px-2 py-0.5 rounded"
                        >
                          {g}
                        </span>
                      ))}
                    </div>

                    <div className="space-y-1">
                      <h3 className="font-bold text-foreground group-hover:text-primary transition-colors text-base line-clamp-1">
                        {movie.title}
                      </h3>
                      {/* Explanatory justification sentence */}
                      <p className="text-xs text-muted-foreground/90 leading-relaxed italic line-clamp-2">
                        &ldquo;{movie.explanation}&rdquo;
                      </p>
                    </div>
                  </div>

                  {/* Actions / Interactions Panel */}
                  <div className="flex items-center justify-between border-t border-border/60 mt-5 pt-4">
                    <span className="text-[10px] text-muted-foreground uppercase font-semibold">
                      Match: <span className="text-primary font-bold">{(movie.final_score * 100).toFixed(0)}%</span>
                    </span>

                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => handleRate(movie.movie_id, "rating", 5.0)}
                        className={`p-1.5 rounded-full hover:bg-primary/10 hover:text-primary transition-colors cursor-pointer ${
                          ratingState === "liked" ? "text-primary bg-primary/10" : "text-muted-foreground"
                        }`}
                        title="Thumb up"
                      >
                        <ThumbsUp className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleRate(movie.movie_id, "skip")}
                        className={`p-1.5 rounded-full hover:bg-red-500/10 hover:text-red-400 transition-colors cursor-pointer ${
                          ratingState === "disliked" ? "text-red-400 bg-red-500/10" : "text-muted-foreground"
                        }`}
                        title="Skip movie"
                      >
                        <ThumbsDown className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleRate(movie.movie_id, "bookmark")}
                        className={`p-1.5 rounded-full hover:bg-secondary/10 hover:text-secondary transition-colors cursor-pointer ${
                          ratingState === "bookmarked" ? "text-secondary bg-secondary/10" : "text-muted-foreground"
                        }`}
                        title="Add to Watchlist"
                      >
                        <Bookmark className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

    </div>
  );
}

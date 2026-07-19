"use client";

import { useRecommendations } from "@/hooks/useRecommendations";
import { useAuth } from "@/providers/AuthProvider";
import { LoadingUI } from "@/components/LoadingUI";
import { ErrorUI } from "@/components/ErrorUI";
import { MovieCard } from "@/components/MovieCard";
import { RecommendationExplanation } from "@/components/RecommendationExplanation";
import { 
  Sparkles, 
  Tv, 
  Activity, 
  BarChart, 
  Clock, 
  Heart 
} from "lucide-react";
import { useState } from "react";

export default function RecommendationsDashboard() {
  const { user } = useAuth();
  const userId = user?.id || "guest_user";

  const { 
    recommendations, 
    isLoading, 
    isError, 
    error, 
    refetch, 
    submitFeedback, 
    userProfile 
  } = useRecommendations(userId, 8);

  const [ratedMovies, setRatedMovies] = useState<Record<number, string>>({});

  const handleRate = async (movieId: number, type: "click" | "skip" | "bookmark") => {
    try {
      await submitFeedback({ movieId, interactionType: type });
      setRatedMovies((prev) => ({
        ...prev,
        [movieId]: type === "click" ? "liked" : type === "skip" ? "skipped" : "saved"
      }));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto py-6">
      
      {/* Top Banner Dashboard */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-6 rounded-2xl border border-border bg-[#0b0c10]/40">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight">Personalization Center</h1>
          <p className="text-xs text-muted-foreground">
            Monitor match parameters calibrated to user <span className="font-semibold text-primary">{userId}</span>.
          </p>
        </div>

        <button 
          onClick={() => refetch()}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl border border-primary/20 bg-primary/10 text-xs font-semibold text-primary hover:bg-primary/20 transition-all cursor-pointer"
        >
          <Activity className="h-4 w-4 animate-spin" />
          Re-calibrate Feed
        </button>
      </div>

      {/* Model Stats Panels */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-xl border border-border bg-[#0b0c10]/20 p-4 flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
            <Heart className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[10px] text-muted-foreground font-medium uppercase">Total Interactions</p>
            <p className="text-lg font-bold text-foreground">{userProfile?.interaction_count || 0}</p>
          </div>
        </div>
        <div className="rounded-xl border border-border bg-[#0b0c10]/20 p-4 flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-secondary/10 flex items-center justify-center text-secondary">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[10px] text-muted-foreground font-medium uppercase">Active Variant</p>
            <p className="text-lg font-bold text-foreground">A/B Testing Group A</p>
          </div>
        </div>
        <div className="rounded-xl border border-border bg-[#0b0c10]/20 p-4 flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
            <BarChart className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[10px] text-muted-foreground font-medium uppercase">Demographic Affinity</p>
            <p className="text-lg font-bold text-foreground">US Core Catalog</p>
          </div>
        </div>
        <div className="rounded-xl border border-border bg-[#0b0c10]/20 p-4 flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-secondary/10 flex items-center justify-center text-secondary">
            <Clock className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[10px] text-muted-foreground font-medium uppercase">Decay Half-Life</p>
            <p className="text-lg font-bold text-foreground">30 Days</p>
          </div>
        </div>
      </div>

      {/* Main recommendation splits */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left 2 Columns: Movie recommendations feed list */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-lg font-bold tracking-wide flex items-center gap-2">
            <Tv className="h-5 w-5 text-primary" />
            Recommended For You
          </h2>

          {isLoading ? (
            <LoadingUI variant="skeleton" />
          ) : isError ? (
            <ErrorUI message={error?.message || "RAG engine is offline."} onRetry={() => refetch()} />
          ) : recommendations.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center text-muted-foreground border border-dashed border-border rounded-xl">
              <Tv className="h-10 w-10 mb-3 text-muted-foreground/45" />
              <p className="text-xs">No active recommendations in store.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {recommendations.map((movie) => (
                <div key={movie.movie_id} className="space-y-3">
                  <MovieCard 
                    movie={{
                      tmdb_id: movie.movie_id,
                      title: movie.title,
                      score: movie.final_score,
                      confidence: movie.final_score,
                      matched_by_sources: ["collaborative_filtering", "graph_proximity"],
                      metadata: {
                        genres: movie.genres,
                        overview: movie.explanation
                      }
                    }} 
                    onFeedback={(id, t) => handleRate(id, t as any)}
                  />
                  
                  {/* Detailed explanation banner */}
                  <RecommendationExplanation 
                    explanationText={movie.explanation} 
                    confidence={movie.final_score} 
                    sources={["CollaborativeCosineCF", "Neo4jGraphWalk", "MaximalGenreDiversity"]} 
                  />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right 1 Column: Taste weights and affinity progress */}
        <div className="lg:col-span-1 space-y-6">
          <h2 className="text-lg font-bold tracking-wide">Taste Profile Metrics</h2>
          
          <div className="rounded-xl border border-border bg-[#0b0c10]/40 p-6 space-y-5">
            {isLoading ? (
              <p className="text-xs text-muted-foreground animate-pulse">Loading profiles...</p>
            ) : userProfile && Object.keys(userProfile.genre_weights || {}).length > 0 ? (
              Object.entries(userProfile.genre_weights).map(([genre, weight]) => {
                const pct = Math.round(weight * 100);
                return (
                  <div key={genre} className="space-y-1.5 text-xs">
                    <div className="flex justify-between font-semibold">
                      <span>{genre}</span>
                      <span className="text-primary">{pct > 0 ? `+${pct}%` : `${pct}%`}</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-[#06070a] border border-border overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-primary to-secondary rounded-full" 
                        style={{ width: `${Math.max(0, Math.min(100, pct))}%` }}
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <p className="text-xs text-muted-foreground">
                Rate films to populate personalized genre weights coordinates.
              </p>
            )}
          </div>
        </div>

      </div>

    </div>
  );
}

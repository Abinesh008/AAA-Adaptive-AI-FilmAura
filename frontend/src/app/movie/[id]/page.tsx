"use client";

import { useMovie } from "@/hooks/useMovie";
import { MovieDetailsSkeleton } from "@/components/LoadingSkeletons";
import { ErrorUI } from "@/components/ErrorUI";
import { useParams, useRouter } from "next/navigation";
import { 
  Tv, 
  Calendar, 
  Clock, 
  Globe, 
  User, 
  Award, 
  ArrowLeft,
  Play,
  Film
} from "lucide-react";
import Link from "next/link";

export default function MovieDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const idStr = Array.isArray(params.id) ? params.id[0] : params.id;
  const movieId = parseInt(idStr || "0", 10);

  const { movie, isLoading, isError, error, refetch } = useMovie(movieId);

  if (isLoading) {
    return <MovieDetailsSkeleton />;
  }

  if (isError || !movie) {
    return (
      <div className="space-y-6">
        <button 
          onClick={() => router.back()}
          className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground font-semibold cursor-pointer"
        >
          <ArrowLeft className="h-4 w-4" />
          Go Back
        </button>
        <ErrorUI 
          message={error?.message || `Movie with ID #${movieId} was not found in active database nodes.`} 
          onRetry={() => refetch()} 
        />
      </div>
    );
  }

  const backdrop = movie.metadata?.backdrop_path || "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&auto=format&fit=crop&q=80";
  const poster = movie.metadata?.poster_path || "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=500&auto=format&fit=crop&q=80";

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      
      {/* Back navigation button */}
      <button 
        onClick={() => router.back()}
        className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground font-semibold cursor-pointer transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Return to Catalog
      </button>

      {/* Cinematic Banner Backdrop */}
      <div className="relative rounded-2xl h-72 md:h-96 w-full overflow-hidden border border-border">
        <img 
          src={backdrop} 
          alt={movie.title}
          className="h-full w-full object-cover" 
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#06070a] via-[#06070a]/40 to-transparent" />
        
        {/* Play Trailer Trigger overlay button */}
        <div className="absolute inset-0 flex items-center justify-center">
          <button className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/95 text-primary-foreground hover:scale-105 transition-all shadow-[0_0_20px_rgba(102,252,241,0.4)] cursor-pointer">
            <Play className="h-6 w-6 fill-current ml-1" />
          </button>
        </div>
      </div>

      {/* Profile Detail Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        {/* Left Side: Poster and Streamers info */}
        <div className="md:col-span-1 space-y-6">
          <div className="rounded-2xl overflow-hidden border border-border shadow-xl">
            <img src={poster} alt={movie.title} className="w-full object-cover" />
          </div>

          {/* Streaming providers */}
          <div className="rounded-xl border border-border bg-[#0b0c10]/40 p-5 space-y-3">
            <h4 className="text-xs font-bold text-foreground uppercase tracking-wide">Streaming Providers</h4>
            <div className="flex flex-wrap gap-2 pt-1.5">
              {movie.metadata?.streaming_providers?.map((provider) => (
                <span 
                  key={provider} 
                  className="px-2.5 py-1 rounded bg-[#06070a] border border-border text-[9px] font-bold text-primary"
                >
                  {provider}
                </span>
              )) || <span className="text-[10px] text-muted-foreground">Digital Purchase Only</span>}
            </div>
          </div>
        </div>

        {/* Right Side: Description and Meta Tags */}
        <div className="md:col-span-2 space-y-6">
          <div className="space-y-3">
            <h1 className="text-3xl font-extrabold tracking-tight">{movie.title}</h1>
            
            <div className="flex flex-wrap gap-4 text-xs text-muted-foreground pt-1">
              <span className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                {movie.metadata?.release_date || "Unknown date"}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                {movie.metadata?.runtime || 120} mins
              </span>
              <span className="flex items-center gap-1">
                <Globe className="h-4 w-4" />
                {movie.metadata?.country || "United States"}
              </span>
            </div>
          </div>

          <div className="space-y-4 pt-4 border-t border-border/50">
            <h3 className="font-bold text-base text-foreground">Synopsis</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {movie.metadata?.overview}
            </p>
          </div>

          {/* Director & Cast grids */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4">
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Director</h4>
              <div className="flex items-center gap-2 p-3.5 rounded-xl border border-border bg-[#0b0c10]/20">
                <User className="h-4 w-4 text-primary" />
                <span className="text-xs font-semibold text-foreground">
                  {movie.metadata?.director || "Registry Unknown"}
                </span>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Key Cast members</h4>
              <div className="flex flex-wrap gap-1.5 pt-0.5">
                {movie.metadata?.cast?.map((actor) => (
                  <span 
                    key={actor} 
                    className="flex items-center gap-1 px-3 py-1.5 rounded-xl border border-border bg-[#0b0c10]/20 text-[10px] font-medium"
                  >
                    <User className="h-3 w-3 text-secondary" />
                    {actor}
                  </span>
                )) || <span className="text-[10px] text-muted-foreground">Unknown cast registry</span>}
              </div>
            </div>
          </div>

          {/* User Review placeholder */}
          <div className="rounded-xl border border-border bg-[#0b0c10]/20 p-5 space-y-3">
            <h4 className="text-xs font-bold text-foreground uppercase tracking-wide">User reviews</h4>
            <p className="text-[11px] text-muted-foreground">
              No user reviews written for this film yet. Be the first to express your feedback to feed model weight calculations.
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}

import { useQuery } from "@tanstack/react-query";
import { movieService } from "@/services/api";

export function useMovie(movieId: number) {
  const movieQuery = useQuery({
    queryKey: ["movieDetails", movieId],
    queryFn: () => movieService.getMovieDetails(movieId),
    enabled: !!movieId && movieId > 0,
  });

  return {
    movie: movieQuery.data || null,
    isLoading: movieQuery.isLoading,
    isError: movieQuery.isError,
    error: movieQuery.error,
    refetch: movieQuery.refetch,
  };
}

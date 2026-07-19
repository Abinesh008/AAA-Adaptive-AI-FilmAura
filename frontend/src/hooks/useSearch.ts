import { useQuery } from "@tanstack/react-query";
import { movieService } from "@/services/api";

export function useSearch(
  query: string,
  sessionId?: string,
  profile = "balanced",
  experimentId?: string
) {
  const searchQuery = useQuery({
    queryKey: ["movieSearch", query, sessionId, profile, experimentId],
    queryFn: () => movieService.searchMovies(query, sessionId, profile, experimentId),
    enabled: query.trim().length > 2,
    placeholderData: (previousData) => previousData,
  });

  return {
    status: searchQuery.data?.status || "success",
    disambiguation: searchQuery.data?.disambiguation || null,
    answer: searchQuery.data?.answer || searchQuery.data?.data?.answer || "",
    movies: searchQuery.data?.movies || searchQuery.data?.data?.movies || [],
    isLoading: searchQuery.isLoading || searchQuery.isFetching,
    isError: searchQuery.isError,
    error: searchQuery.error,
    refetch: searchQuery.refetch,
  };
}

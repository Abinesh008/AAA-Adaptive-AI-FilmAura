import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { recommendationService } from "@/services/api";

export function useRecommendations(
  userId: string,
  limit = 10,
  region?: string,
  subscriptionTier = "free",
  isChildProfile = false
) {
  const queryClient = useQueryClient();

  const recommendationsQuery = useQuery({
    queryKey: ["recommendations", userId, limit, region, subscriptionTier, isChildProfile],
    queryFn: () =>
      recommendationService.getRecommendations(
        userId,
        limit,
        region,
        subscriptionTier,
        isChildProfile
      ),
    enabled: !!userId,
  });

  const feedbackMutation = useMutation({
    mutationFn: ({
      movieId,
      interactionType,
      rating,
    }: {
      movieId: number;
      interactionType: string;
      rating?: number;
    }) =>
      recommendationService.submitFeedback(userId, movieId, interactionType, rating),
    onSuccess: () => {
      // Invalidate active recommendations to trigger updates on profile rebuild
      queryClient.invalidateQueries({ queryKey: ["recommendations", userId] });
      queryClient.invalidateQueries({ queryKey: ["userProfile", userId] });
    },
  });

  const userProfileQuery = useQuery({
    queryKey: ["userProfile", userId],
    queryFn: () => recommendationService.getUserProfile(userId),
    enabled: !!userId,
  });

  return {
    recommendations: recommendationsQuery.data?.recommendations || [],
    experimentGroup: recommendationsQuery.data?.experiment_group || "control",
    isLoading: recommendationsQuery.isLoading,
    isError: recommendationsQuery.isError,
    error: recommendationsQuery.error,
    refetch: recommendationsQuery.refetch,
    submitFeedback: feedbackMutation.mutateAsync,
    isSubmittingFeedback: feedbackMutation.isPending,
    userProfile: userProfileQuery.data || null,
    isLoadingProfile: userProfileQuery.isLoading,
  };
}

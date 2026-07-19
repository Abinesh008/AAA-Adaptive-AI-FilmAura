import { useMutation, useQueryClient } from "@tanstack/react-query";
import { recommendationService } from "@/services/api";

export function useFeedback(userId: string) {
  const queryClient = useQueryClient();

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
      queryClient.invalidateQueries({ queryKey: ["recommendations", userId] });
      queryClient.invalidateQueries({ queryKey: ["userProfile", userId] });
    },
  });

  return {
    submitFeedback: feedbackMutation.mutateAsync,
    isLoading: feedbackMutation.isPending,
    isError: feedbackMutation.isError,
    error: feedbackMutation.error,
  };
}

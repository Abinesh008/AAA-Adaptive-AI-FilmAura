import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { agentService } from "@/services/api";

export function useHistory(sessionId: string) {
  const queryClient = useQueryClient();

  const historyQuery = useQuery({
    queryKey: ["agentHistory", sessionId],
    queryFn: () => agentService.getHistory(sessionId),
    enabled: !!sessionId,
  });

  const clearHistoryMutation = useMutation({
    mutationFn: () => agentService.clearHistory(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agentHistory", sessionId] });
    },
  });

  return {
    history: historyQuery.data || [],
    isLoading: historyQuery.isLoading,
    isError: historyQuery.isError,
    error: historyQuery.error,
    clearHistory: clearHistoryMutation.mutateAsync,
    isClearing: clearHistoryMutation.isPending,
  };
}

import { apiClient } from "@/lib/axios";

export interface RecommendationItem {
  movie_id: number;
  title: string;
  final_score: number;
  explanation: string;
  genres: string[];
}

export interface RecommendationResponse {
  user_id: string;
  experiment_group: string;
  recommendations: RecommendationItem[];
  trace_id: string;
}

export interface UserTasteProfile {
  user_id: string;
  genre_weights: Record<string, number>;
  favorite_directors: string[];
  favorite_actors: string[];
  interaction_count: number;
}

export interface AgentMessageRequest {
  user_id: string;
  message: string;
  session_id?: string;
}

export interface AgentMessageResponse {
  answer: string;
  trace_id: string;
  suggested_movies?: Array<{ id: number; title: string }>;
}

export const recommendationService = {
  getRecommendations: async (
    userId: string,
    limit = 10,
    region?: string,
    subscriptionTier = "free",
    isChildProfile = false
  ): Promise<RecommendationResponse> => {
    const params = new URLSearchParams();
    params.append("limit", limit.toString());
    if (region) params.append("region", region);
    params.append("subscription_tier", subscriptionTier);
    params.append("is_child_profile", isChildProfile.toString());

    const response = await apiClient.post<RecommendationResponse>(
      `/api/v1/recommendations/retrieve?${params.toString()}`,
      {},
      {
        headers: {
          "user-id": userId,
        },
      }
    );
    return response.data;
  },

  submitFeedback: async (
    userId: string,
    movieId: number,
    interactionType: string,
    rating?: number
  ): Promise<void> => {
    await apiClient.post(
      "/api/v1/recommendations/feedback",
      {
        movie_id: movieId,
        interaction_type: interactionType,
        rating,
      },
      {
        headers: {
          "user-id": userId,
        },
      }
    );
  },

  getUserProfile: async (userId: string): Promise<UserTasteProfile> => {
    const response = await apiClient.get<UserTasteProfile>(
      `/api/v1/recommendations/profile/${userId}`
    );
    return response.data;
  },
};

export const agentService = {
  sendMessage: async (
    userId: string,
    message: string,
    sessionId?: string
  ): Promise<AgentMessageResponse> => {
    // Phase 4 Agent POST endpoint maps to /api/v1/agent/query
    const response = await apiClient.post<AgentMessageResponse>(
      "/api/v1/agent/query",
      {
        user_id: userId,
        message: message,
        session_id: sessionId || userId,
      }
    );
    return response.data;
  },
};

export const authService = {
  // Stubs for future authentication layers
  login: async () => {
    return { success: true, user: { id: "guest_user", name: "Guest User" } };
  },
  logout: async () => {
    return { success: true };
  },
};

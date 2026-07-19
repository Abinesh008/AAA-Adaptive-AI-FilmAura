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

export interface UserSession {
  id: string;
  email: string;
  name: string;
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

// Client-side authentication simulation storing credentials locally
export const authService = {
  login: async (email: string, password: string): Promise<{ success: boolean; token: string; user: UserSession }> => {
    // Simulate delay
    await new Promise((resolve) => setTimeout(resolve, 800));

    if (typeof window === "undefined") {
      throw new Error("Window context not available.");
    }

    const rawUsers = localStorage.getItem("filmaura_users");
    const users: Array<UserSession & { password?: string }> = rawUsers ? JSON.parse(rawUsers) : [];

    const matchedUser = users.find((u) => u.email.toLowerCase() === email.toLowerCase());
    if (!matchedUser || matchedUser.password !== password) {
      throw new Error("Invalid email or password combination.");
    }

    const token = `mock-jwt-${btoa(JSON.stringify({ email: matchedUser.email, id: matchedUser.id }))}`;
    return {
      success: true,
      token,
      user: {
        id: matchedUser.id,
        email: matchedUser.email,
        name: matchedUser.name,
      },
    };
  },

  register: async (email: string, name: string, password: string): Promise<{ success: boolean }> => {
    await new Promise((resolve) => setTimeout(resolve, 800));

    if (typeof window === "undefined") {
      throw new Error("Window context not available.");
    }

    const rawUsers = localStorage.getItem("filmaura_users");
    const users: Array<UserSession & { password?: string }> = rawUsers ? JSON.parse(rawUsers) : [];

    const emailExists = users.some((u) => u.email.toLowerCase() === email.toLowerCase());
    if (emailExists) {
      throw new Error("An account is already registered with this email address.");
    }

    const newId = email.split("@")[0].replace(/[^a-zA-Z0-9]/g, "_");
    users.push({
      id: newId,
      email,
      name,
      password,
    });

    localStorage.setItem("filmaura_users", JSON.stringify(users));
    return { success: true };
  },

  getCurrentUser: async (token: string): Promise<UserSession> => {
    if (!token || !token.startsWith("mock-jwt-")) {
      throw new Error("Malformed authorization token.");
    }

    const jsonStr = atob(token.replace("mock-jwt-", ""));
    const decoded = JSON.parse(jsonStr);

    const rawUsers = localStorage.getItem("filmaura_users");
    const users: Array<UserSession> = rawUsers ? JSON.parse(rawUsers) : [];
    const matched = users.find((u) => u.email.toLowerCase() === decoded.email.toLowerCase());

    if (!matched) {
      throw new Error("Session user record not found.");
    }

    return matched;
  },

  logout: async (): Promise<{ success: boolean }> => {
    return { success: true };
  },
};

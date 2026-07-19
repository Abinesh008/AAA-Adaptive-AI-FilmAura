import { apiClient } from "@/lib/axios";

// ----------------------------------------------------
// Type Interfaces
// ----------------------------------------------------

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

export interface ProvenanceChain {
  database: string;
  table_or_label?: string;
  node_id_or_vector_id?: string;
  query_executed?: string;
  confidence_contribution: number;
}

export interface CandidateMovie {
  tmdb_id: number;
  title: string;
  score: number;
  confidence: number;
  matched_by_sources: string[];
  provenance_details?: ProvenanceChain[];
  metadata: {
    genres?: string[];
    overview?: string;
    runtime?: number;
    release_date?: string;
    vote_average?: number;
    poster_path?: string;
    backdrop_path?: string;
    director?: string;
    cast?: string[];
    country?: string;
    language?: string;
    streaming_providers?: string[];
    [key: string]: any;
  };
}

export interface SearchResponse {
  status: "success" | "ambiguous";
  disambiguation?: any;
  answer?: string;
  movies?: CandidateMovie[];
  data?: {
    answer: string;
    movies: CandidateMovie[];
    trace_id: string;
    confidence_score: number;
    confidence_breakdown: Record<string, number>;
  };
}

export interface AgentChatMessage {
  role: "user" | "assistant" | "agent";
  content: string;
}

export interface UserSession {
  id: string;
  email: string;
  name: string;
}

// ----------------------------------------------------
// 1. Recommendation & Feedback Services
// ----------------------------------------------------
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

// ----------------------------------------------------
// 2. Agent Conversational Services
// ----------------------------------------------------
export const agentService = {
  sendMessage: async (
    query: string,
    sessionId?: string
  ): Promise<{ status: string; data: { content: string; trace_id?: string } }> => {
    const response = await apiClient.post<{ status: string; data: { content: string; trace_id?: string } }>(
      "/api/v1/agent/chat",
      {
        query,
        session_id: sessionId,
      }
    );
    return response.data;
  },

  getHistory: async (sessionId: string): Promise<AgentChatMessage[]> => {
    const response = await apiClient.get<{ history: AgentChatMessage[] }>(
      `/api/v1/agent/history/${sessionId}`
    );
    return response.data.history || [];
  },

  clearHistory: async (sessionId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/agent/history/${sessionId}`);
  },
};

// ----------------------------------------------------
// 3. Movie Discovery & Retrieval Services
// ----------------------------------------------------
export const movieService = {
  searchMovies: async (
    query: string,
    sessionId?: string,
    profile = "balanced",
    experimentId?: string
  ): Promise<SearchResponse> => {
    const params = new URLSearchParams();
    params.append("query", query);
    if (sessionId) params.append("session_id", sessionId);
    params.append("profile", profile);
    if (experimentId) params.append("experiment_id", experimentId);

    const response = await apiClient.post<SearchResponse>(
      `/api/v1/retrieval/search?${params.toString()}`
    );
    return response.data;
  },

  // Fallback dynamic generator to present stunning details for mock visual pages
  getMovieDetails: async (movieId: number): Promise<CandidateMovie> => {
    // 1. Simulate brief details loading
    await new Promise((resolve) => setTimeout(resolve, 300));

    // A predefined list of cinema items to feed details. If requested ID is not in here, we generate dynamically
    const catalog: Record<number, CandidateMovie> = {
      27205: {
        tmdb_id: 27205,
        title: "Inception",
        score: 0.95,
        confidence: 0.98,
        matched_by_sources: ["postgres", "neo4j", "chromadb"],
        metadata: {
          genres: ["Sci-Fi", "Action", "Thriller"],
          overview: "Cobb, a skilled thief who commits corporate espionage by infiltrating the sub-conscious of his targets, is offered a chance to regain his old life as payment for a task considered to be impossible: \"inception\", the implantation of another person's idea into a target's subconscious.",
          runtime: 148,
          release_date: "2010-07-16",
          vote_average: 8.4,
          poster_path: "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=500&auto=format&fit=crop&q=80",
          backdrop_path: "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&auto=format&fit=crop&q=80",
          director: "Christopher Nolan",
          cast: ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page", "Tom Hardy"],
          country: "United States",
          language: "English",
          streaming_providers: ["Netflix", "HBO Max", "Amazon Prime Video"],
        }
      },
      157336: {
        tmdb_id: 157336,
        title: "Interstellar",
        score: 0.93,
        confidence: 0.96,
        matched_by_sources: ["postgres", "neo4j"],
        metadata: {
          genres: ["Sci-Fi", "Drama", "Adventure"],
          overview: "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel and conquer the vast distances involved in an interstellar voyage.",
          runtime: 169,
          release_date: "2014-11-07",
          vote_average: 8.3,
          poster_path: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500&auto=format&fit=crop&q=80",
          backdrop_path: "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=1200&auto=format&fit=crop&q=80",
          director: "Christopher Nolan",
          cast: ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain", "Michael Caine"],
          country: "United States",
          language: "English",
          streaming_providers: ["Paramount+", "Amazon Prime Video"],
        }
      }
    };

    if (catalog[movieId]) {
      return catalog[movieId];
    }

    // Default dynamic generator fallback
    return {
      tmdb_id: movieId,
      title: `Cinematic Match #${movieId}`,
      score: 0.88,
      confidence: 0.85,
      matched_by_sources: ["chromadb"],
      metadata: {
        genres: ["Drama", "Mystery"],
        overview: "An immersive sensory analysis tracking intricate character nodes, emotional visual cues, and narrative themes within the FilmAura adaptive model matrix.",
        runtime: 124,
        release_date: "2023-10-12",
        vote_average: 7.9,
        poster_path: "https://images.unsplash.com/photo-1542204172-e7052809f852?w=500&auto=format&fit=crop&q=80",
        backdrop_path: "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&auto=format&fit=crop&q=80",
        director: "Alex Garland",
        cast: ["Cailee Spaeny", "Kirsten Dunst", "Wagner Moura"],
        country: "United States",
        language: "English",
        streaming_providers: ["Apple TV", "Google Play"],
      }
    };
  }
};

// ----------------------------------------------------
// 4. Client-side Authentication Services (Simulated)
// ----------------------------------------------------
export const authService = {
  login: async (email: string, password: string): Promise<{ success: boolean; token: string; user: UserSession }> => {
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

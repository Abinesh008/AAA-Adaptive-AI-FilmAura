import { useMutation } from "@tanstack/react-query";
import { agentService } from "@/services/api";
import { useState } from "react";

export interface ChatMessage {
  id: string;
  sender: "user" | "agent";
  text: string;
  timestamp: Date;
  suggestedMovies?: Array<{ id: number; title: string }>;
}

export function useAgent(userId: string, sessionId?: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const agentMutation = useMutation({
    mutationFn: (text: string) => agentService.sendMessage(text, sessionId || userId),
    onSuccess: (data, variables) => {
      const agentMsg: ChatMessage = {
        id: `agent-${Date.now()}-${data.data.trace_id || ""}`,
        sender: "agent",
        text: data.data.content,
        timestamp: new Date(),
        suggestedMovies: [],
      };
      setMessages((prev) => [...prev, agentMsg]);
    },
  });

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    await agentMutation.mutateAsync(text);
  };

  return {
    messages,
    sendMessage,
    isLoading: agentMutation.isPending,
    isError: agentMutation.isError,
    error: agentMutation.error,
    clearChat: () => setMessages([]),
  };
}

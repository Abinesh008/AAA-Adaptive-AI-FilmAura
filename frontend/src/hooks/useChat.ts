import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { agentService, AgentChatMessage } from "@/services/api";
import { useState, useEffect, useRef } from "react";

export interface ChatMessage {
  id: string;
  sender: "user" | "agent";
  text: string;
  timestamp: Date;
}

export function useChat(userId: string, sessionId?: string) {
  const activeSessionId = sessionId || userId;
  const queryClient = useQueryClient();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  
  // Abort controller reference to cancel active HTTP requests
  const abortControllerRef = useRef<AbortController | null>(null);

  // 1. Fetch historical conversations on session mount
  const { data: history = [], isLoading: isLoadingHistory } = useQuery({
    queryKey: ["agentHistory", activeSessionId],
    queryFn: () => agentService.getHistory(activeSessionId),
    enabled: !!activeSessionId,
  });

  useEffect(() => {
    if (history.length > 0) {
      const parsedMsgs: ChatMessage[] = history.map((h, index) => ({
        id: `history-${index}-${Date.now()}`,
        sender: h.role === "user" ? "user" : "agent",
        text: h.content,
        timestamp: new Date(),
      }));
      setMessages(parsedMsgs);
    } else {
      setMessages([]);
    }
  }, [history]);

  const agentMutation = useMutation({
    mutationFn: async (text: string) => {
      // Create new abort controller
      abortControllerRef.current = new AbortController();
      
      const response = await agentService.sendMessage(text, activeSessionId);
      return response.data;
    },
    onSuccess: (data) => {
      // Stream text character-by-character for a premium typing aesthetic
      setIsStreaming(true);
      const fullText = data.content;
      let currentIndex = 0;
      
      const tempId = `agent-stream-${Date.now()}`;
      setMessages((prev) => [
        ...prev,
        { id: tempId, sender: "agent", text: "", timestamp: new Date() }
      ]);

      const interval = setInterval(() => {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === tempId
              ? { ...msg, text: fullText.substring(0, currentIndex + 2) }
              : msg
          )
        );
        currentIndex += 3; // stream 3 characters per tick

        if (currentIndex >= fullText.length) {
          clearInterval(interval);
          setIsStreaming(false);
          // Invalidate history query to keep backend aligned
          queryClient.invalidateQueries({ queryKey: ["agentHistory", activeSessionId] });
        }
      }, 20);
    },
  });

  const sendMessage = async (text: string) => {
    if (!text.trim() || agentMutation.isPending || isStreaming) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    await agentMutation.mutateAsync(text);
  };

  const stopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsStreaming(false);
    agentMutation.reset();
  };

  const regenerateResponse = async () => {
    // Find last user message in the thread
    const userMsgs = messages.filter((m) => m.sender === "user");
    if (userMsgs.length === 0) return;
    const lastUserText = userMsgs[userMsgs.length - 1].text;
    
    // Remove the last agent message from view if present
    setMessages((prev) => {
      const lastIndex = prev.map(m => m.sender).lastIndexOf("agent");
      if (lastIndex !== -1) {
        return prev.filter((_, idx) => idx !== lastIndex);
      }
      return prev;
    });

    await agentMutation.mutateAsync(lastUserText);
  };

  const clearChat = async () => {
    setMessages([]);
    await agentService.clearHistory(activeSessionId);
    queryClient.invalidateQueries({ queryKey: ["agentHistory", activeSessionId] });
  };

  return {
    messages,
    sendMessage,
    stopGeneration,
    regenerateResponse,
    clearChat,
    isLoading: agentMutation.isPending || isLoadingHistory,
    isStreaming,
    isError: agentMutation.isError,
    error: agentMutation.error,
  };
}

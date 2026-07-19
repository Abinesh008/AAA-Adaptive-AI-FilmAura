"use client";

import { useChat } from "@/hooks/useChat";
import { useAuth } from "@/providers/AuthProvider";
import { 
  MessageSquare, 
  Send, 
  Sparkles, 
  User, 
  Trash2, 
  Square, 
  RotateCcw, 
  Copy, 
  Check,
  ChevronRight
} from "lucide-react";
import { useState, useRef, useEffect } from "react";

export default function ChatPage() {
  const { user } = useAuth();
  const userId = user?.id || "guest_user";
  
  const { 
    messages, 
    sendMessage, 
    stopGeneration, 
    regenerateResponse, 
    clearChat, 
    isLoading, 
    isStreaming 
  } = useChat(userId);

  const [input, setInput] = useState("");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, isStreaming]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || isStreaming) return;
    const text = input;
    setInput("");
    await sendMessage(text);
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const suggestedPrompts = [
    "Recommend a mind-bending sci-fi movie with memory-loss twists.",
    "Recommend space exploration films featuring a strong musical score.",
    "Recommend slow-burn thriller films from directors like Christopher Nolan."
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)] border border-border bg-[#0b0c10]/40 rounded-2xl overflow-hidden backdrop-blur-sm">
      
      {/* Chat header panel */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-[#0b0c10]/60">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 border border-primary/20 text-primary">
            <MessageSquare className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-foreground">AI Research Companion</h2>
            <p className="text-[10px] text-muted-foreground flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
              {isStreaming ? "Streaming response..." : "Reasoning Engine Ready"}
            </p>
          </div>
        </div>
        {messages.length > 0 && (
          <button 
            onClick={clearChat}
            className="p-2 rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground transition-colors cursor-pointer"
            title="Clear conversation history"
          >
            <Trash2 className="h-4.5 w-4.5" />
          </button>
        )}
      </div>

      {/* Messages thread viewport */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-6 max-w-lg mx-auto">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 border border-primary/20 text-primary shadow-[0_0_15px_rgba(102,252,241,0.05)]">
              <Sparkles className="h-6 w-6" />
            </div>
            
            <div className="space-y-2">
              <h3 className="font-bold text-foreground text-sm">Welcome to FilmAura Agent</h3>
              <p className="text-xs text-muted-foreground leading-relaxed max-w-sm">
                Describe a mood, plot archetype, or director choice to query recommendations.
              </p>
            </div>

            {/* Suggested quick clicks */}
            <div className="w-full space-y-2 pt-2">
              {suggestedPrompts.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => setInput(p)}
                  className="w-full flex items-center justify-between text-left p-3 rounded-xl border border-border bg-[#0b0c10]/20 hover:bg-[#0b0c10]/60 text-[11px] text-muted-foreground hover:text-foreground transition-all duration-200 cursor-pointer group"
                >
                  <span className="truncate pr-4">{p}</span>
                  <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-primary group-hover:translate-x-0.5 transition-all shrink-0" />
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => {
            const isUser = msg.sender === "user";
            return (
              <div 
                key={msg.id}
                className={`flex gap-4 max-w-2xl group ${isUser ? "ml-auto flex-row-reverse" : ""}`}
              >
                <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full border text-xs font-semibold ${
                  isUser 
                    ? "bg-secondary/10 border-secondary/20 text-secondary" 
                    : "bg-primary/10 border-primary/20 text-primary"
                }`}>
                  {isUser ? <User className="h-4 w-4" /> : <Sparkles className="h-4 w-4" />}
                </div>

                <div className="space-y-1.5 flex-1">
                  <div className={`p-4 rounded-2xl text-xs leading-relaxed ${
                    isUser 
                      ? "bg-secondary/10 border border-secondary/20 text-foreground rounded-tr-none" 
                      : "bg-[#131520]/80 border border-border text-foreground rounded-tl-none"
                  }`}>
                    {msg.text}
                  </div>

                  {/* Actions under message bubble */}
                  {!isUser && msg.text.trim().length > 0 && (
                    <div className="flex items-center gap-2 text-[9px] text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity pl-2">
                      <button 
                        onClick={() => handleCopy(msg.id, msg.text)}
                        className="flex items-center gap-1 hover:text-foreground cursor-pointer"
                        title="Copy text"
                      >
                        {copiedId === msg.id ? <Check className="h-3 w-3 text-green-400" /> : <Copy className="h-3 w-3" />}
                        {copiedId === msg.id ? "Copied" : "Copy"}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}

        {/* Loading/Streaming indicators */}
        {isLoading && !isStreaming && (
          <div className="flex gap-4 max-w-2xl">
            <div className="flex h-9 w-9 items-center justify-center rounded-full border border-primary/20 bg-primary/10 text-primary">
              <Sparkles className="h-4 w-4" />
            </div>
            <div className="flex items-center gap-1.5 p-4 rounded-2xl bg-[#131520]/80 border border-border rounded-tl-none text-[10px] text-muted-foreground">
              <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
              Thinking...
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input / Control triggers panel */}
      <div className="p-4 border-t border-border bg-[#0b0c10]/60 space-y-3">
        {/* Streaming controls */}
        {(isStreaming || isLoading) && (
          <div className="flex justify-center gap-3">
            <button
              onClick={stopGeneration}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border bg-[#06070a] text-[10px] font-semibold text-red-400 hover:bg-red-500/10 hover:border-red-500/20 transition-all cursor-pointer"
            >
              <Square className="h-3 w-3 fill-red-400" />
              Stop response
            </button>
            {!isLoading && messages.length > 0 && (
              <button
                onClick={regenerateResponse}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border bg-[#06070a] text-[10px] font-semibold text-primary hover:bg-primary/10 hover:border-primary/20 transition-all cursor-pointer"
              >
                <RotateCcw className="h-3 w-3" />
                Regenerate
              </button>
            )}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about movies, plot developments, or settings..."
            className="flex-1 h-11 px-4 rounded-xl border border-border bg-[#06070a] text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary transition-all duration-200"
            disabled={isLoading || isStreaming}
          />
          <button
            type="submit"
            disabled={isLoading || isStreaming || !input.trim()}
            className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50 transition-all glow-btn cursor-pointer"
          >
            <Send className="h-4.5 w-4.5" />
          </button>
        </form>
      </div>

    </div>
  );
}

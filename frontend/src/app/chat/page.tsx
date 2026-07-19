"use client";

import { useAgent } from "@/hooks/useAgent";
import { useAuth } from "@/providers/AuthProvider";
import { MessageSquare, Send, Sparkles, User, Tv, Trash2 } from "lucide-react";
import { useState, useRef, useEffect } from "react";

export default function ChatPage() {
  const { user } = useAuth();
  const userId = user?.id || "guest_user";
  const { messages, sendMessage, isLoading, clearChat } = useAgent(userId);
  const [input, setInput] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to latest message bubble
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    const text = input;
    setInput("");
    await sendMessage(text);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)] border border-border bg-[#0b0c10]/40 rounded-2xl overflow-hidden">
      
      {/* Top chat status header bar */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-[#0b0c10]/60">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 border border-primary/20 text-primary">
            <MessageSquare className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-foreground">AI Research Companion</h2>
            <p className="text-[10px] text-muted-foreground flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
              Reasoning Engine Ready
            </p>
          </div>
        </div>
        {messages.length > 0 && (
          <button 
            onClick={clearChat}
            className="p-2 rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground transition-colors cursor-pointer"
            title="Clear Chat history"
          >
            <Trash2 className="h-4.5 w-4.5" />
          </button>
        )}
      </div>

      {/* Messages viewport */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4 max-w-sm mx-auto">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 border border-primary/20 text-primary">
              <Sparkles className="h-6 w-6" />
            </div>
            <h3 className="font-bold text-foreground text-sm">Ask FilmAura Agent</h3>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Describe your mood, search movies by themes, actors, twists, or request a complete reasoning calibration. E.g.
              <br />
              <span className="italic text-primary/80 mt-1 block">&ldquo;Recommend a mind-bending sci-fi movie similar to Inception.&rdquo;</span>
            </p>
          </div>
        ) : (
          messages.map((msg) => {
            const isUser = msg.sender === "user";
            return (
              <div 
                key={msg.id}
                className={`flex gap-4 max-w-2xl ${isUser ? "ml-auto flex-row-reverse" : ""}`}
              >
                {/* Avatar icon */}
                <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full border text-xs font-semibold ${
                  isUser 
                    ? "bg-secondary/10 border-secondary/20 text-secondary" 
                    : "bg-primary/10 border-primary/20 text-primary"
                }`}>
                  {isUser ? <User className="h-4 w-4" /> : <Sparkles className="h-4 w-4" />}
                </div>

                {/* Message bubble content */}
                <div className="space-y-3">
                  <div className={`p-4 rounded-2xl text-xs leading-relaxed ${
                    isUser 
                      ? "bg-secondary/10 border border-secondary/20 text-foreground rounded-tr-none" 
                      : "bg-[#131520]/80 border border-border text-foreground rounded-tl-none"
                  }`}>
                    {msg.text}
                  </div>

                  {/* Recommendations attachment block */}
                  {!isUser && msg.suggestedMovies && msg.suggestedMovies.length > 0 && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
                      {msg.suggestedMovies.map((movie) => (
                        <div 
                          key={movie.id}
                          className="flex items-center gap-2 p-2.5 rounded-lg border border-border bg-[#0b0c10]/40 text-[10px]"
                        >
                          <Tv className="h-4 w-4 text-primary shrink-0" />
                          <span className="font-semibold text-foreground line-clamp-1">{movie.title}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}

        {/* Streaming loader indicator */}
        {isLoading && (
          <div className="flex gap-4 max-w-2xl">
            <div className="flex h-9 w-9 items-center justify-center rounded-full border border-primary/20 bg-primary/10 text-primary">
              <Sparkles className="h-4 w-4" />
            </div>
            <div className="flex items-center gap-1.5 p-4 rounded-2xl bg-[#131520]/80 border border-border rounded-tl-none">
              <span className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }} />
              <span className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "150ms" }} />
              <span className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "300ms" }} />
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Message input panel */}
      <form 
        onSubmit={handleSubmit}
        className="p-4 border-t border-border bg-[#0b0c10]/60 flex gap-3"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about movies, plot devices, actors, or settings..."
          className="flex-1 h-11 px-4 rounded-xl border border-border bg-[#06070a] text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary transition-all duration-200"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50 transition-all glow-btn cursor-pointer"
        >
          <Send className="h-4.5 w-4.5" />
        </button>
      </form>
      
    </div>
  );
}

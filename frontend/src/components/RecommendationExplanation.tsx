"use client";

import { Info, Sparkles, Database } from "lucide-react";

interface RecommendationExplanationProps {
  explanationText: string;
  confidence: number;
  sources: string[];
}

export function RecommendationExplanation({
  explanationText,
  confidence,
  sources,
}: RecommendationExplanationProps) {
  return (
    <div className="rounded-xl border border-border bg-[#0b0c10]/30 p-4 space-y-3">
      
      {/* Title / Header */}
      <div className="flex items-center justify-between text-xs font-semibold text-foreground">
        <span className="flex items-center gap-1.5 text-primary">
          <Sparkles className="h-4 w-4" />
          AI Explanation Justification
        </span>
        <span className="text-[10px] text-muted-foreground">
          Confidence: <span className="text-foreground font-bold">{Math.round(confidence * 100)}%</span>
        </span>
      </div>

      {/* Justification text */}
      <p className="text-xs text-muted-foreground leading-relaxed italic">
        &ldquo;{explanationText}&rdquo;
      </p>

      {/* Inferred nodes info */}
      <div className="flex items-center gap-2 pt-2 border-t border-border/40 text-[9px] text-muted-foreground">
        <Database className="h-3.5 w-3.5 text-secondary" />
        <span>Resolved Path:</span>
        <div className="flex flex-wrap gap-1.5">
          {sources.map((src) => (
            <span key={src} className="bg-muted px-1.5 py-0.5 rounded text-[8px] uppercase tracking-wider font-semibold">
              {src}
            </span>
          ))}
        </div>
      </div>
      
    </div>
  );
}

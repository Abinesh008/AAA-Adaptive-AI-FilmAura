"use client";

import Link from "next/link";
import { Film } from "lucide-react";

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="w-full border-t border-border bg-[#06070a] py-6 px-8 mt-auto">
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand */}
        <div className="flex items-center gap-2">
          <Film className="h-4 w-4 text-primary" />
          <span className="text-sm font-semibold tracking-wider bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            FilmAura
          </span>
          <span className="text-[10px] text-muted-foreground ml-2">v5.0.0 Stable</span>
        </div>

        {/* Links */}
        <div className="flex items-center gap-6 text-xs text-muted-foreground">
          <Link href="/" className="hover:text-foreground transition-colors">Feed</Link>
          <Link href="/chat" className="hover:text-foreground transition-colors">Chat</Link>
          <Link href="/terms" className="hover:text-foreground transition-colors">Terms</Link>
          <Link href="/privacy" className="hover:text-foreground transition-colors">Privacy</Link>
        </div>

        {/* Footprint */}
        <div className="text-[10px] text-muted-foreground">
          &copy; {year} FilmAura. Adaptive AI Recommendation Systems.
        </div>
      </div>
    </footer>
  );
}

"use client";

import { Menu, Search, Film, Bell } from "lucide-react";
import Link from "next/link";
import { useAuth } from "@/providers/AuthProvider";

interface HeaderProps {
  onMenuOpen: () => void;
}

export function Header({ onMenuOpen }: HeaderProps) {
  const { user } = useAuth();
  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-border bg-[#06070a]/80 backdrop-blur-md px-6">
      
      {/* Left side: Mobile Menu Trigger & Logo */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuOpen}
          className="lg:hidden p-2 rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Brand showing on mobile top only */}
        <Link href="/" className="flex items-center gap-2 lg:hidden">
          <Film className="h-5 w-5 text-primary" />
          <span className="font-bold text-lg tracking-wider text-foreground">FilmAura</span>
        </Link>
      </div>

      {/* Middle: Search bar placeholder */}
      <div className="hidden sm:flex max-w-md w-full mx-8">
        <div className="relative w-full">
          <Search className="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Ask AI or search movies semantically..."
            className="w-full h-10 pl-10 pr-4 rounded-full border border-border bg-[#0b0c10] text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all duration-200"
            disabled
          />
        </div>
      </div>

      {/* Right side: Action triggers */}
      <div className="flex items-center gap-4">
        {/* Metric indicator badge */}
        <div className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full border border-primary/20 bg-primary/5 text-[10px] font-semibold text-primary shadow-[0_0_8px_rgba(102,252,241,0.05)]">
          <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
          AI Engine Online
        </div>

        <button className="relative p-2 rounded-full text-muted-foreground hover:bg-muted hover:text-foreground transition-colors">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-secondary shadow-[0_0_8px_#9d4edd]" />
        </button>

        {/* User quick status */}
        <Link 
          href="/account"
          className="h-9 w-9 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center font-bold text-primary text-sm cursor-pointer hover:border-primary transition-colors"
        >
          {user?.name?.substring(0, 1).toUpperCase() || "G"}
        </Link>
      </div>
    </header>
  );
}

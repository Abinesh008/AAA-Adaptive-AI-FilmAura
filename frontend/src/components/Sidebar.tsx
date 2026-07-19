"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  Film, 
  Sparkles, 
  MessageSquare, 
  Search, 
  Bookmark, 
  Settings,
  X
} from "lucide-react";
import { cn } from "@/utils/cn"; // we will create a simple utils class for className merging

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  const navItems = [
    {
      name: "AI Recommendations",
      href: "/",
      icon: Sparkles,
    },
    {
      name: "AI Chat Agent",
      href: "/chat",
      icon: MessageSquare,
    },
    {
      name: "Semantic Search",
      href: "/search",
      icon: Search,
    },
    {
      name: "Watchlist",
      href: "/watchlist",
      icon: Bookmark,
    },
    {
      name: "Settings",
      href: "/settings",
      icon: Settings,
    },
  ];

  return (
    <>
      {/* Backdrop for mobile drawer */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar container */}
      <aside
        className={cn(
          "fixed top-0 bottom-0 left-0 z-50 flex w-72 flex-col border-r border-border bg-[#0b0c10]/95 backdrop-blur-md transition-transform duration-300 lg:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Header / Brand */}
        <div className="flex h-16 items-center justify-between px-6 border-b border-border">
          <Link href="/" className="flex items-center gap-2" onClick={onClose}>
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 border border-primary/20 text-primary">
              <Film className="h-5 w-5 animate-pulse" />
            </div>
            <span className="text-xl font-bold tracking-wider bg-gradient-to-r from-primary via-cyan-400 to-secondary bg-clip-text text-transparent">
              FilmAura
            </span>
          </Link>
          <button 
            onClick={onClose}
            className="lg:hidden p-1.5 rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation list */}
        <nav className="flex-1 space-y-1.5 px-4 py-6 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onClose}
                className={cn(
                  "flex items-center gap-3.5 px-4 py-3 rounded-lg text-sm font-medium transition-all group duration-200",
                  isActive 
                    ? "bg-primary/10 border border-primary/20 text-primary" 
                    : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                )}
              >
                <Icon className={cn(
                  "h-5 w-5 transition-transform duration-200 group-hover:scale-105",
                  isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                )} />
                <span>{item.name}</span>
                {isActive && (
                  <span className="ml-auto h-1.5 w-1.5 rounded-full bg-primary shadow-[0_0_8px_#66fcf1]" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Footer/User profile quick links */}
        <div className="p-4 border-t border-border bg-[#06070a]/50">
          <div className="flex items-center gap-3 px-2 py-1.5">
            <div className="h-9 w-9 rounded-full bg-secondary/20 border border-secondary/30 flex items-center justify-center font-bold text-secondary text-sm">
              GU
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-semibold text-foreground">Guest User</span>
              <span className="text-[10px] text-muted-foreground">Standard Member</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

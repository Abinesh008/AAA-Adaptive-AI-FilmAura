"use client";

import { useAuth } from "@/providers/AuthProvider";
import { useRecommendations } from "@/hooks/useRecommendations";
import { User, Mail, Shield, LogOut, Award, Layers } from "lucide-react";

export default function AccountPage() {
  const { user, token, logout } = useAuth();
  const userId = user?.id || "guest_user";
  
  const { userProfile, isLoadingProfile } = useRecommendations(userId);

  return (
    <div className="space-y-8 max-w-4xl mx-auto py-6">
      
      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-2xl font-bold tracking-tight">Your Account</h1>
        <p className="text-sm text-muted-foreground">
          View your session authentication tokens and adaptive taste coordinates.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left Side: Avatar and Info Card */}
        <div className="md:col-span-1 rounded-xl border border-border bg-[#0b0c10]/40 p-6 flex flex-col items-center text-center space-y-4">
          <div className="h-20 w-20 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center font-bold text-primary text-3xl shadow-[0_0_20px_rgba(102,252,241,0.1)]">
            {user?.name?.substring(0, 2).toUpperCase() || "GU"}
          </div>
          
          <div className="space-y-1">
            <h3 className="font-bold text-foreground text-base">{user?.name || "Guest User"}</h3>
            <p className="text-xs text-muted-foreground">{user?.email || "guest@example.com"}</p>
          </div>

          <div className="w-full pt-4 border-t border-border/60">
            <button
              onClick={logout}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-red-500/20 bg-red-500/10 text-xs font-semibold text-red-400 hover:bg-red-500/20 transition-all cursor-pointer"
            >
              <LogOut className="h-4 w-4" />
              Sign Out
            </button>
          </div>
        </div>

        {/* Right Side: Detailed coordinates & Token stats */}
        <div className="md:col-span-2 space-y-6">
          
          {/* Active Session & Security details */}
          <div className="rounded-xl border border-border bg-[#0b0c10]/40 p-6 space-y-4">
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <Shield className="h-4.5 w-4.5 text-primary" />
              Active Session Metadata
            </h3>
            
            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-1.5 border-b border-border/40">
                <span className="text-muted-foreground">User ID</span>
                <span className="font-mono text-foreground">{userId}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-border/40">
                <span className="text-muted-foreground">Security Token</span>
                <span className="font-mono text-primary/80 line-clamp-1 max-w-[200px] truncate" title={token || ""}>
                  {token || "No token stored"}
                </span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-muted-foreground">Session Tier</span>
                <span className="font-semibold text-secondary flex items-center gap-1">
                  <Award className="h-4 w-4 text-secondary" />
                  Standard Account
                </span>
              </div>
            </div>
          </div>

          {/* Taste coordinates detail */}
          <div className="rounded-xl border border-border bg-[#0b0c10]/40 p-6 space-y-4">
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <Layers className="h-4.5 w-4.5 text-secondary" />
              Taste coordinates overview
            </h3>

            {isLoadingProfile ? (
              <p className="text-xs text-muted-foreground animate-pulse">Loading vectors...</p>
            ) : userProfile && Object.keys(userProfile.genre_weights || {}).length > 0 ? (
              <div className="space-y-3 text-xs">
                {Object.entries(userProfile.genre_weights).map(([genre, weight]) => {
                  const percent = Math.round(weight * 100);
                  return (
                    <div key={genre} className="space-y-1">
                      <div className="flex justify-between text-[11px]">
                        <span className="text-foreground font-medium">{genre}</span>
                        <span className="text-primary font-bold">{percent > 0 ? `+${percent}%` : `${percent}%`}</span>
                      </div>
                      <div className="h-1.5 w-full bg-[#06070a] rounded-full overflow-hidden border border-border">
                        <div 
                          className="h-full bg-primary rounded-full" 
                          style={{ width: `${Math.max(0, Math.min(100, percent))}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">
                No taste affinity profiles registered yet. Rate movies on your feed or chat with the AI assistant to populate coordinates.
              </p>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}

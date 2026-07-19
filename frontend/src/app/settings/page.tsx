"use client";

import { Settings, Shield, Globe, Award } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="space-y-8 max-w-4xl mx-auto py-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-bold tracking-tight">System Settings</h1>
        <p className="text-sm text-muted-foreground">
          Calibrate recommendations and regional filter policies.
        </p>
      </div>

      <div className="space-y-6">
        
        {/* Region & Licensing */}
        <div className="rounded-xl border border-border bg-[#0b0c10]/40 p-6 space-y-4">
          <h3 className="text-sm font-semibold flex items-center gap-2">
            <Globe className="h-4.5 w-4.5 text-primary" />
            Regional constraints
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="space-y-1.5">
              <label className="text-muted-foreground">Country Catalog</label>
              <select className="w-full h-10 rounded bg-[#06070a] border border-border px-3 text-foreground" disabled>
                <option>United States (US)</option>
                <option>United Kingdom (UK)</option>
                <option>Canada (CA)</option>
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-muted-foreground">Subscription tier</label>
              <select className="w-full h-10 rounded bg-[#06070a] border border-border px-3 text-foreground" disabled>
                <option>Free member</option>
                <option>Premium tier</option>
              </select>
            </div>
          </div>
        </div>

        {/* Content protections */}
        <div className="rounded-xl border border-border bg-[#0b0c10]/40 p-6 space-y-4">
          <h3 className="text-sm font-semibold flex items-center gap-2">
            <Shield className="h-4.5 w-4.5 text-secondary" />
            Safety filters
          </h3>
          <div className="flex items-center justify-between text-xs py-2">
            <div>
              <p className="font-semibold text-foreground">Age restricts (Child Profile)</p>
              <p className="text-[10px] text-muted-foreground mt-0.5">Filter out adult rated content from recommendation runs.</p>
            </div>
            <input type="checkbox" className="h-5 w-5 rounded border-border accent-primary bg-[#06070a]" disabled />
          </div>
        </div>

      </div>
    </div>
  );
}

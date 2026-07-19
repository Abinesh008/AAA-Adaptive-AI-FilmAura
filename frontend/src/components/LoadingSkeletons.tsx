"use client";

export function MovieCardSkeleton() {
  return (
    <div className="h-72 rounded-xl border border-border bg-[#0b0c10]/40 p-4 space-y-4 animate-pulse">
      <div className="aspect-[16/10] w-full rounded bg-muted" />
      <div className="space-y-2">
        <div className="h-5 w-2/3 rounded bg-muted" />
        <div className="h-4 w-full rounded bg-muted" />
        <div className="h-4 w-5/6 rounded bg-muted" />
      </div>
    </div>
  );
}

export function MovieGridSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 w-full">
      {Array.from({ length: count }).map((_, idx) => (
        <MovieCardSkeleton key={idx} />
      ))}
    </div>
  );
}

export function MovieDetailsSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="h-64 md:h-80 w-full rounded-xl bg-muted" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1 h-80 rounded-xl bg-muted" />
        <div className="md:col-span-2 space-y-4">
          <div className="h-8 w-1/3 rounded bg-muted" />
          <div className="h-6 w-2/3 rounded bg-muted" />
          <div className="space-y-2 pt-4">
            <div className="h-4 w-full rounded bg-muted" />
            <div className="h-4 w-full rounded bg-muted" />
            <div className="h-4 w-3/4 rounded bg-muted" />
          </div>
        </div>
      </div>
    </div>
  );
}

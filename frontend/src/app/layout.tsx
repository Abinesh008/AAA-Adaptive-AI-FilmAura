import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { AppProviders } from "@/providers";
import { DashboardLayout } from "@/components/DashboardLayout";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "FilmAura - Adaptive AI Movie Recommendations",
  description: "Experience hyper-personalized film recommendations powered by advanced collaborative filtering, graph modeling, and AI reasoning agent layers.",
  keywords: ["movie recommendation", "AI movie finder", "collaborative filtering", "graph walk", "adaptive AI"],
  authors: [{ name: "FilmAura Team" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`} suppressHydrationWarning>
      <body className="min-h-full bg-background text-foreground flex flex-col font-sans">
        <AppProviders>
          <DashboardLayout>{children}</DashboardLayout>
        </AppProviders>
      </body>
    </html>
  );
}

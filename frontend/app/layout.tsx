import "../styles/globals.css";
import React from "react";
import { SpeedInsights } from '@vercel/speed-insights/next';

export const metadata = {
  title: "CodeLens",
  description: "AI Code Review",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
      <SpeedInsights />
    </html>
  );
}

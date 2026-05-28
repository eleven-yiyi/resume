import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BossJob AI",
  description: "AI-powered job matching for Southeast Asia",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 min-h-screen text-sm antialiased">
        {children}
      </body>
    </html>
  );
}

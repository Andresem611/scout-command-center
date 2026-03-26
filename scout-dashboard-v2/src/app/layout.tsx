import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Scout Command Center",
  description: "Agent dashboard for Thoven outreach",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-gray-950 text-gray-100`}>
        <div className="min-h-screen">
          <nav className="border-b border-gray-800 bg-gray-900/50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-16">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🎯</span>
                  <span className="font-semibold text-lg">Scout Command Center</span>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-400">
                  <a href="/" className="hover:text-white transition">Dashboard</a>
                  <a href="/pipeline" className="hover:text-white transition">Pipeline</a>
                  <a href="/morning-batch" className="hover:text-white transition">Morning Batch</a>
                </div>
              </div>
            </div>
          </nav>
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

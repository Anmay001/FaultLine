import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Sidebar from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "FaultLine — Multi-Agent Risk & Failure Detection",
  description:
    "Autonomous agentic software project failure intelligence platform powered by deterministic AST, static analysis, test inspection, and ground-truth verification.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-black text-zinc-100 antialiased flex flex-col selection:bg-white selection:text-black">
        <Navbar />
        <div className="flex-1 flex w-full max-w-[1600px] mx-auto">
          <Sidebar />
          <main className="flex-1 min-w-0 p-6 md:p-8 overflow-y-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

import type { Metadata, Viewport } from "next";
import { Outfit, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Sidebar from "@/components/Sidebar";
import Footer from "@/components/Footer";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "FaultLine — Multi-Agent Risk & Failure Detection",
  description:
    "Autonomous agentic software project failure intelligence platform powered by deterministic AST, static analysis, test inspection, and ground-truth verification.",
  metadataBase: new URL("https://faultline.dev"),
  openGraph: {
    title: "FaultLine — Multi-Agent Risk & Failure Detection",
    description:
      "Autonomous agentic software project failure intelligence platform powered by deterministic AST, static analysis, test inspection, and ground-truth verification.",
    type: "website",
    siteName: "FaultLine",
  },
  twitter: {
    card: "summary_large_image",
    title: "FaultLine — Multi-Agent Risk & Failure Detection",
    description:
      "Autonomous agentic software project failure intelligence platform.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  themeColor: "#000000",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`dark ${outfit.variable} ${jetbrainsMono.variable}`} suppressHydrationWarning>
      <body className="min-h-screen bg-black text-zinc-100 antialiased flex flex-col selection:bg-white selection:text-black">
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        <Navbar />
        <div className="flex-1 flex w-full max-w-[1600px] mx-auto flex-col">
          <div className="flex-1 flex">
            <Sidebar />
            <main id="main-content" className="flex-1 min-w-0 p-6 md:p-8 overflow-y-auto" tabIndex={-1}>
              {children}
            </main>
          </div>
          <Footer />
        </div>
      </body>
    </html>
  );
}

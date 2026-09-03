import type { Metadata, Viewport } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Sidebar from "@/components/Sidebar";
import Footer from "@/components/Footer";

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
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="preload" as="font" type="font/woff2" crossOrigin="anonymous" href="https://fonts.gstatic.com/s/outfit/v15/QGYsz_wNahGAdqQ43RhVcDYK4pc.woff2" />
        <link rel="preload" as="font" type="font/woff2" crossOrigin="anonymous" href="https://fonts.gstatic.com/s/jetbrainsmono/v25/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKk.woff2" />
      </head>
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

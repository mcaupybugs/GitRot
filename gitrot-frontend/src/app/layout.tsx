import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { LayoutWrapper } from "@/components/LayoutWrapper";
import { AuthProvider } from "@/components/AuthProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "GitRot - AI-Powered README Generator",
  description:
    "Transform your GitHub repositories into professional, comprehensive documentation with AI. Generate beautiful READMEs instantly using Azure OpenAI.",
  keywords: [
    "README generator",
    "GitHub",
    "AI",
    "documentation",
    "Azure OpenAI",
    "markdown",
    "repository",
  ],
  authors: [{ name: "GitRot Team" }],
  creator: "Mcaupybugs",
  publisher: "Mcaupybugs",
  metadataBase: new URL("https://gitrot.vercel.app"),
  openGraph: {
    title: "GitRot - AI-Powered README Generator",
    description:
      "Transform your GitHub repositories into professional, comprehensive documentation with AI.",
    url: "https://gitrot.vercel.app",
    siteName: "GitRot",
    type: "website",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "GitRot - AI-Powered README Generator",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "GitRot - AI-Powered README Generator",
    description:
      "Transform your GitHub repositories into professional, comprehensive documentation with AI.",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
    },
  },
  verification: {
    google: "your-google-verification-code",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <AuthProvider>
          <LayoutWrapper>{children}</LayoutWrapper>
        </AuthProvider>
      </body>
    </html>
  );
}

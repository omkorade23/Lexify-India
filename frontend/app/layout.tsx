import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Lexify India — Legal Document Intelligence",
    template: "%s | Lexify India",
  },
  description:
    "Upload your legal document. Ask questions. Get grounded answers with exact citations from your document and Indian law — powered by AI.",
  keywords: ["legal document", "AI", "India", "rental agreement", "contract analysis", "RAG"],
  authors: [{ name: "Lexify India" }],
  openGraph: {
    title: "Lexify India — Legal Document Intelligence",
    description: "AI-powered legal document understanding for Indian citizens",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}

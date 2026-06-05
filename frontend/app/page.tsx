import type { Metadata } from "next";
import LandingNav from "@/components/landing/LandingNav";
import HeroSection from "@/components/landing/HeroSection";
import DocumentTypeCards from "@/components/landing/DocumentTypeCards";
import HowItWorks from "@/components/landing/HowItWorks";
import FeatureHighlights from "@/components/landing/FeatureHighlights";
import Footer from "@/components/landing/Footer";

export const metadata: Metadata = {
  title: "Lexify India — AI Legal Assistant for India",
  description:
    "Ask legal questions and get grounded answers. Upload legal documents for clause-by-clause analysis powered by AI and Indian law knowledge base.",
};

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-bg-base">
      <LandingNav />
      <main>
        <HeroSection />

        <div id="document-types">
          <DocumentTypeCards />
        </div>

        <div id="how-it-works">
          <HowItWorks />
        </div>

        <div id="features">
          <FeatureHighlights />
        </div>
      </main>

      <Footer />
    </div>
  );
}

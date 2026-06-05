import React from "react";
import { FileText, Briefcase, Home, FileSignature, Scale, Shield } from "lucide-react";

const DOCUMENT_TYPES = [
  { icon: Home, label: "Rental Agreement", description: "Understand your rights as a tenant or landlord" },
  { icon: Briefcase, label: "Employment Contract", description: "Know your notice period, benefits, and clauses" },
  { icon: Shield, label: "NDA", description: "Identify what you can and cannot disclose" },
  { icon: FileText, label: "Property Deed", description: "Verify ownership terms and encumbrances" },
  { icon: Scale, label: "Legal Notice", description: "Understand demands and response timelines" },
  { icon: FileSignature, label: "Affidavit", description: "Know what you are declaring under oath" },
];

export default function DocumentTypeCards() {
  return (
    <section id="documents" className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-center text-text-primary text-3xl font-bold mb-3">
          Supported Document Types
        </h2>
        <p className="text-center text-text-secondary mb-12">
          Upload any common Indian legal document and start asking questions instantly
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {DOCUMENT_TYPES.map(({ icon: Icon, label, description }) => (
            <div
              key={label}
              className="group flex items-start gap-4 bg-bg-surface border border-border-default hover:border-border-hover hover:bg-bg-elevated rounded-2xl p-5 transition-all duration-200"
            >
              <div className="w-10 h-10 rounded-xl bg-[rgba(34,197,94,0.10)] flex items-center justify-center shrink-0">
                <Icon size={20} className="text-accent" />
              </div>
              <div>
                <p className="text-text-primary font-semibold text-[14px] mb-1">{label}</p>
                <p className="text-text-secondary text-[13px] leading-relaxed">{description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

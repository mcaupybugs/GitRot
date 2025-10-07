"use client";

import * as React from "react";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { cn } from "@/lib/utils";

interface LayoutWrapperProps {
  children: React.ReactNode;
}

export function LayoutWrapper({ children }: LayoutWrapperProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  // Close mobile menu when clicking outside
  React.useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }

    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isMobileMenuOpen]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 to-stone-100">
      <Topbar onMenuClick={toggleMobileMenu} />

      {/* Desktop Sidebar */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {/* Mobile Sidebar Overlay */}
      {isMobileMenuOpen && (
        <>
          <div
            className="fixed inset-0 bg-black/20 z-20 lg:hidden"
            onClick={toggleMobileMenu}
          />
          <div className="lg:hidden">
            <Sidebar />
          </div>
        </>
      )}

      {/* Main Content - Always has left padding for sidebar on desktop */}
      <main
        className={cn(
          "pt-16 transition-all duration-300 ease-in-out",
          "lg:pt-16 lg:pl-16"
        )}
      >
        {children}
      </main>
    </div>
  );
}

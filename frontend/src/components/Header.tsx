import React, { useState } from "react";
import {
  Activity,
  ShieldAlert,
  Cpu,
  BookOpen,
  Layers,
  BarChart3,
  GitCompare,
  Menu,
  X,
} from "lucide-react";

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  serverHealthy: boolean;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, serverHealthy }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const tabs = [
    { id: "home", label: "Overview", icon: BookOpen },
    { id: "recommender", label: "Assessment", icon: Activity },
    { id: "comparison", label: "RST vs ML", icon: GitCompare },
    { id: "rst_theory", label: "RST Theory", icon: Layers },
    { id: "rules", label: "Rules", icon: Cpu },
    { id: "benchmarks", label: "Benchmarks", icon: BarChart3 },
  ];

  const handleTabClick = (tabId: string) => {
    setActiveTab(tabId);
    setMobileMenuOpen(false);
  };

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
      {/* Top Academic Disclaimer Banner */}
      <div className="bg-amber-950/30 border-b border-amber-900/40 px-3 sm:px-4 py-1.5 text-xs text-amber-300/90 flex items-center justify-between">
        <div className="flex items-center gap-2 max-w-5xl mx-auto w-full">
          <ShieldAlert className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          {/* Desktop/Tablet text */}
          <span className="hidden sm:inline">
            <strong>Academic Research Decision-Support Prototype:</strong> For educational & computational evaluation only. NOT a clinical medical diagnostic system.
          </span>
          {/* Mobile compact text */}
          <span className="sm:hidden text-[11px] font-medium">
            Academic prototype · Not for clinical diagnosis
          </span>
        </div>
        <div className="flex items-center gap-1.5 shrink-0 pl-2">
          <span className={`inline-block w-2 h-2 rounded-full ${serverHealthy ? "bg-emerald-400 animate-pulse" : "bg-rose-500"}`} />
          <span className="text-[11px] text-slate-400 font-mono hidden md:inline">
            {serverHealthy ? "Engine Active (4,920 records)" : "Engine Offline"}
          </span>
        </div>
      </div>

      {/* Main Header Brand */}
      <div className="max-w-7xl mx-auto px-4 py-2.5 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-brand-500/20 shrink-0">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm sm:text-base font-bold text-white tracking-tight flex items-center gap-2">
                Rough Set Intelligent Recommender
                <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-400 border border-brand-500/20 hidden sm:inline-block">
                  RST + Rules + ML
                </span>
              </h1>
            </div>
            <p className="text-[11px] sm:text-xs text-slate-400 line-clamp-1">
              Intelligent Decision-Support from Incomplete Symptom Sets using Rough Set Theory
            </p>
          </div>
        </div>

        {/* Desktop Navigation Tabs */}
        <nav className="hidden lg:flex items-center gap-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                data-tab={tab.id}
                onClick={() => handleTabClick(tab.id)}
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap cursor-pointer ${
                  isActive
                    ? "bg-brand-500/15 text-brand-400 border border-brand-500/30 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? "text-brand-400" : "text-slate-400"}`} />
                {tab.label}
              </button>
            );
          })}
        </nav>

        {/* Mobile / Tablet Hamburger Button */}
        <button
          id="mobile-menu-btn"
          data-testid="mobile-menu-btn"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="lg:hidden p-2 rounded-lg bg-slate-900 text-slate-300 hover:text-white border border-slate-800 transition-colors cursor-pointer"
          aria-label="Toggle Navigation Menu"
        >
          {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Mobile Navigation Dropdown / Drawer */}
      {mobileMenuOpen && (
        <div
          id="mobile-menu-drawer"
          className="lg:hidden border-t border-slate-800 bg-slate-950/95 backdrop-blur-xl px-4 py-3 flex flex-col gap-1.5 animate-fadeIn shadow-2xl"
        >
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                data-tab={tab.id}
                onClick={() => handleTabClick(tab.id)}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium transition-all w-full text-left cursor-pointer ${
                  isActive
                    ? "bg-brand-500/15 text-brand-400 border border-brand-500/30 shadow-sm font-bold"
                    : "text-slate-300 hover:text-white hover:bg-slate-900 border border-transparent"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-brand-400" : "text-slate-400"}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
};

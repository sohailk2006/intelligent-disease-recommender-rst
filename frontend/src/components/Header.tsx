import React from "react";
import { Activity, ShieldAlert, Cpu, BookOpen, Layers, BarChart3, GitCompare } from "lucide-react";

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  serverHealthy: boolean;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, serverHealthy }) => {
  const tabs = [
    { id: "home", label: "Overview", icon: BookOpen },
    { id: "recommender", label: "Symptom Assessment", icon: Activity },
    { id: "comparison", label: "RST vs ML Lab", icon: GitCompare },
    { id: "rst_theory", label: "Rough Set & Reducts", icon: Layers },
    { id: "rules", label: "Association Rules", icon: Cpu },
    { id: "benchmarks", label: "Faculty Benchmarks", icon: BarChart3 },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
      {/* Top Academic Disclaimer Banner */}
      <div className="bg-amber-950/30 border-b border-amber-900/40 px-4 py-1.5 text-xs text-amber-300/90 flex items-center justify-between">
        <div className="flex items-center gap-2 max-w-5xl mx-auto w-full">
          <ShieldAlert className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span>
            <strong>Academic Research Decision-Support Prototype:</strong> For educational & computational decision-support evaluation only. NOT a clinical medical diagnostic system.
          </span>
        </div>
        <div className="flex items-center gap-2 shrink-0 pr-4">
          <span className={`inline-block w-2 h-2 rounded-full ${serverHealthy ? "bg-emerald-400 animate-pulse" : "bg-rose-500"}`} />
          <span className="text-[11px] text-slate-400 font-mono">
            {serverHealthy ? "Engine Active (4,920 records)" : "Engine Offline"}
          </span>
        </div>
      </div>

      {/* Main Header Brand */}
      <div className="max-w-7xl mx-auto px-4 py-3 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                Rough Set Intelligent Recommender
                <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-400 border border-brand-500/20">
                  RST + Rules + ML
                </span>
              </h1>
            </div>
            <p className="text-xs text-slate-400 line-clamp-1">
              Deterministic Disease Prediction from Incomplete Symptom Sets using Pawlak Rough Set Theory
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap ${
                  isActive
                    ? "bg-brand-500/15 text-brand-400 border border-brand-500/30 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? "text-brand-400" : "text-slate-500"}`} />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};

import React from "react";
import {
  Activity,
  Layers,
  TrendingUp,
  Cpu,
  ShieldAlert,
  ArrowRight,
  Database,
  FileCode2,
  BarChart3,
} from "lucide-react";
import type { SystemMetadata } from "../types";

interface HomeViewProps {
  onStartAssessment: () => void;
  onExploreBenchmarks: () => void;
  onExploreTheory: () => void;
  metadata: SystemMetadata | null;
}

export const HomeView: React.FC<HomeViewProps> = ({
  onStartAssessment,
  onExploreBenchmarks,
  onExploreTheory,
  metadata,
}) => {
  return (
    <div className="flex flex-col gap-6 animate-fadeIn max-w-6xl mx-auto py-2">
      {/* Hero Section */}
      <div className="glass-panel rounded-3xl p-6 sm:p-10 border border-slate-800 relative overflow-hidden shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col gap-5 max-w-4xl">
          {/* Academic Badge */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="px-3 py-1 rounded-full bg-brand-500/15 text-brand-400 border border-brand-500/30 text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5" />
              Academic Research Prototype
            </span>
          </div>

          {/* Project Title & Short Subtitle */}
          <div>
            <h1 className="text-lg sm:text-2xl lg:text-3xl font-bold sm:font-extrabold text-white tracking-tight leading-snug sm:leading-tight">
              An Intelligent Recommender System Using Machine Learning, Association Rules and Rough Set for Disease Prediction from Incomplete Symptom Set
            </h1>
            <p className="text-xs sm:text-base text-slate-300 mt-2 font-medium">
              Recommend diseases from incomplete symptom information using Rough Set Theory.
            </p>
          </div>

          {/* Academic Prototype Disclaimer */}
          <div className="p-3 rounded-2xl bg-amber-950/20 border border-amber-800/40 text-xs text-amber-200/90 flex items-center gap-2.5">
            <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
            <span className="font-medium text-amber-200">
              Academic prototype · Decision-support only · Not for clinical diagnosis
            </span>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center gap-3 pt-1">
            <button
              onClick={onStartAssessment}
              className="px-5 py-3 rounded-xl bg-gradient-to-r from-brand-600 via-indigo-600 to-brand-500 hover:from-brand-500 hover:to-indigo-500 text-white font-bold text-xs uppercase tracking-wider shadow-lg shadow-brand-500/25 flex items-center gap-2 transition-all cursor-pointer"
            >
              <Activity className="w-4 h-4" />
              <span>Start Symptom Assessment</span>
              <ArrowRight className="w-4 h-4 ml-0.5" />
            </button>

            <button
              onClick={onExploreBenchmarks}
              className="px-4 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 hover:text-white border border-slate-700/80 font-semibold text-xs flex items-center gap-2 transition-all cursor-pointer"
            >
              <BarChart3 className="w-4 h-4 text-brand-400" />
              <span>View Faculty Benchmarks</span>
            </button>

            <button
              onClick={onExploreTheory}
              className="px-4 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 hover:text-white border border-slate-700/80 font-semibold text-xs flex items-center gap-2 transition-all cursor-pointer"
            >
              <FileCode2 className="w-4 h-4 text-indigo-400" />
              <span>RST Reducts & Math</span>
            </button>
          </div>
        </div>
      </div>

      {/* Triad Architecture: 3 Concise Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Card 1: Rough Sets */}
        <div className="glass-panel rounded-2xl p-5 border border-brand-500/30 bg-slate-900/50 flex flex-col justify-between gap-3 h-full">
          <div>
            <div className="w-9 h-9 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400 mb-2.5">
              <Layers className="w-4 h-4" />
            </div>
            <span className="text-[10px] font-bold text-brand-400 uppercase tracking-wider block">
              Core Method
            </span>
            <h3 className="text-sm font-bold text-white mt-0.5">
              Rough Sets
            </h3>
            <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">
              Primary reasoning method for incomplete symptoms.
            </p>
          </div>
        </div>

        {/* Card 2: Association Rules */}
        <div className="glass-panel rounded-2xl p-5 border border-slate-800 bg-slate-900/50 flex flex-col justify-between gap-3 h-full">
          <div>
            <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-2.5">
              <TrendingUp className="w-4 h-4" />
            </div>
            <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider block">
              Supporting Component
            </span>
            <h3 className="text-sm font-bold text-white mt-0.5">
              Association Rules
            </h3>
            <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">
              Finds symptom combinations associated with disease outcomes.
            </p>
          </div>
        </div>

        {/* Card 3: ML Comparison */}
        <div className="glass-panel rounded-2xl p-5 border border-slate-800 bg-slate-900/50 flex flex-col justify-between gap-3 h-full">
          <div>
            <div className="w-9 h-9 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-2.5">
              <Cpu className="w-4 h-4" />
            </div>
            <span className="text-[10px] font-bold text-purple-400 uppercase tracking-wider block">
              Comparative Baselines
            </span>
            <h3 className="text-sm font-bold text-white mt-0.5">
              ML Comparison
            </h3>
            <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">
              Compares robustness under missing symptom information.
            </p>
          </div>
        </div>
      </div>

      {/* Dataset Summary Card (Displayed exactly once on Home) */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col gap-3">
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-brand-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            Dataset Summary
          </h3>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 uppercase block">Training Records</span>
            <span className="text-base font-bold text-white font-mono mt-0.5 block">
              {metadata?.dataset_summary.universe_size ?? 4920}
            </span>
          </div>

          <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 uppercase block">Test Records</span>
            <span className="text-base font-bold text-white font-mono mt-0.5 block">
              42
            </span>
          </div>

          <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 uppercase block">Symptoms</span>
            <span className="text-base font-bold text-white font-mono mt-0.5 block">
              {metadata?.dataset_summary.num_condition_attributes ?? 132}
            </span>
          </div>

          <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 uppercase block">Diseases</span>
            <span className="text-base font-bold text-white font-mono mt-0.5 block">
              {metadata?.dataset_summary.num_decision_classes ?? 41}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

import React from "react";
import {
  Activity,
  Layers,
  TrendingUp,
  Cpu,
  ShieldAlert,
  ArrowRight,
  Database,
  CheckCircle2,
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
    <div className="flex flex-col gap-8 animate-fadeIn max-w-6xl mx-auto py-2">
      {/* Hero Section */}
      <div className="glass-panel rounded-3xl p-8 sm:p-12 border border-slate-800 relative overflow-hidden shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col gap-6 max-w-4xl">
          {/* Academic Badge */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="px-3 py-1 rounded-full bg-brand-500/15 text-brand-400 border border-brand-500/30 text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5" />
              B.Tech Major / Mini Project AI/ML Research Prototype
            </span>
            <span className="px-3 py-1 rounded-full bg-slate-900 text-slate-400 border border-slate-800 text-xs font-mono">
              Pawlak Rough Set Theory (1982)
            </span>
          </div>

          {/* Project Title */}
          <div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight">
              An Intelligent Recommender System Using Machine Learning, Association Rules and Rough Set for Disease Prediction from Incomplete Symptom Set
            </h1>
            <p className="text-base sm:text-lg text-slate-300 mt-4 leading-relaxed font-medium">
              Intelligent disease recommendation from incomplete symptom information using Rough Set Theory.
            </p>
          </div>

          {/* Academic / Research Disclaimer */}
          <div className="p-4 rounded-2xl bg-amber-950/20 border border-amber-800/40 text-xs text-amber-200/90 flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <strong className="block font-bold text-amber-300 text-sm mb-0.5">
                Academic Research Prototype Disclaimer
              </strong>
              This system is an academic decision-support prototype and is not a clinical diagnostic tool. It is engineered to mathematically evaluate and demonstrate how Rough Set Theory reasons over incomplete, unobserved symptom sets without forced zero-imputation.
            </div>
          </div>

          {/* CTAs */}
          <div className="flex flex-wrap items-center gap-4 pt-2">
            <button
              onClick={onStartAssessment}
              className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-brand-600 via-indigo-600 to-brand-500 hover:from-brand-500 hover:to-indigo-500 text-white font-bold text-sm uppercase tracking-wider shadow-lg shadow-brand-500/25 flex items-center gap-2.5 transition-all cursor-pointer"
            >
              <Activity className="w-4 h-4" />
              <span>Start Symptom Assessment</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </button>

            <button
              onClick={onExploreBenchmarks}
              className="px-5 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 hover:text-white border border-slate-700/80 font-semibold text-sm flex items-center gap-2 transition-all cursor-pointer"
            >
              <BarChart3 className="w-4 h-4 text-brand-400" />
              <span>View Faculty Benchmarks</span>
            </button>

            <button
              onClick={onExploreTheory}
              className="px-5 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 hover:text-white border border-slate-700/80 font-semibold text-sm flex items-center gap-2 transition-all cursor-pointer"
            >
              <FileCode2 className="w-4 h-4 text-indigo-400" />
              <span>RST Reducts & Math</span>
            </button>
          </div>
        </div>
      </div>

      {/* Triad Architecture Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Core Method: Rough Set Theory */}
        <div className="glass-panel rounded-2xl p-6 border border-brand-500/30 bg-slate-900/50 flex flex-col justify-between gap-4">
          <div>
            <div className="w-10 h-10 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400 mb-3">
              <Layers className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-bold text-brand-400 uppercase tracking-wider block">
              Primary Reasoning Engine
            </span>
            <h3 className="text-base font-bold text-white mt-0.5">
              Pawlak Rough Set Theory
            </h3>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Functions as the primary deterministic reasoning technique. Formulates a <strong>compatibility/tolerance neighborhood $[q]_T$</strong> comparing only known symptoms. Derives Lower Approximations (certainty) and Boundary Regions (ambiguity) without assuming unobserved symptoms are absent.
            </p>
          </div>
          <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-400">
            <span>Dependency $\gamma$: <strong className="text-brand-400">1.0000</strong></span>
            <span>Minimal Reduct: <strong className="text-brand-400">38 attrs</strong></span>
          </div>
        </div>

        {/* Supporting Component 1: Association Rules */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 bg-slate-900/50 flex flex-col justify-between gap-4">
          <div>
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-3">
              <TrendingUp className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider block">
              Supporting Component 1
            </span>
            <h3 className="text-base font-bold text-white mt-0.5">
              Association Rule Mining
            </h3>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Mined strictly on the training universe using the Apriori algorithm ($min\_support = 0.01$, $min\_confidence = 0.70$). Generates <strong>831 disease-consequent rules</strong> that provide verifiable clinical co-occurrence evidence for candidate predictions.
            </p>
          </div>
          <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-400">
            <span>Mined Rules: <strong className="text-indigo-400">831</strong></span>
            <span>Max Rule Lift: <strong className="text-indigo-400">41.0x</strong></span>
          </div>
        </div>

        {/* Supporting Component 2: ML Baselines */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 bg-slate-900/50 flex flex-col justify-between gap-4">
          <div>
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-3">
              <Cpu className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-bold text-purple-400 uppercase tracking-wider block">
              Supporting Component 2
            </span>
            <h3 className="text-base font-bold text-white mt-0.5">
              Machine Learning Baselines
            </h3>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Provides comparative benchmarks against <strong>Random Forest, Bernoulli Naive Bayes, Logistic Regression, and CART Decision Trees</strong>. Demonstrates empirical fragility when conventional models impute missing values as 0 ($? \to 0$).
            </p>
          </div>
          <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-400">
            <span>RST at 70% missing: <strong className="text-emerald-400">85.24%</strong></span>
            <span>CART at 70%: <strong className="text-rose-400">36.67%</strong></span>
          </div>
        </div>
      </div>

      {/* Dataset & Research Scope Card */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-brand-400" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Empirical Dataset Profile & Verification Scope
            </h3>
          </div>
          <span className="text-[11px] font-mono text-slate-400">
            Zero Data Leakage Guaranteed
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="bg-slate-900/80 p-3.5 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-500 uppercase block">Training Universe</span>
            <span className="text-lg font-bold text-white font-mono">
              {metadata?.dataset_summary.universe_size ?? 4920} records
            </span>
            <span className="text-[10px] text-slate-400 block mt-0.5">
              120 records × 41 diseases
            </span>
          </div>

          <div className="bg-slate-900/80 p-3.5 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-500 uppercase block">Held-Out Test Set</span>
            <span className="text-lg font-bold text-white font-mono">42 records</span>
            <span className="text-[10px] text-amber-400/90 block mt-0.5">
              Empirical evaluation only
            </span>
          </div>

          <div className="bg-slate-900/80 p-3.5 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-500 uppercase block">Condition Attributes</span>
            <span className="text-lg font-bold text-white font-mono">
              {metadata?.dataset_summary.num_condition_attributes ?? 132} symptoms
            </span>
            <span className="text-[10px] text-slate-400 block mt-0.5">
              Homogeneous binary flags (0/1)
            </span>
          </div>

          <div className="bg-slate-900/80 p-3.5 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-500 uppercase block">Decision Classes</span>
            <span className="text-lg font-bold text-white font-mono">
              {metadata?.dataset_summary.num_decision_classes ?? 41} diseases
            </span>
            <span className="text-[10px] text-slate-400 block mt-0.5">
              Full dependency $\gamma = 1.0$
            </span>
          </div>
        </div>

        <div className="text-[11px] text-slate-400 border-t border-slate-800/80 pt-3 flex items-start gap-2">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
          <span>
            <strong>Formal Academic Audit Status:</strong> All mathematical axioms verified. $Testing.csv$ ($N=42$) is strictly held out and excluded from reduct calculation, discernibility analysis, core extraction, rule mining, and ML training.
          </span>
        </div>
      </div>
    </div>
  );
};

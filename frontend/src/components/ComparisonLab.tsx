import React from "react";
import { GitCompare, Layers, Cpu, Clock, ShieldCheck } from "lucide-react";
import type { CompareResponse } from "../types";

interface ComparisonLabProps {
  comparisonData: CompareResponse | null;
  isLoading: boolean;
  onRunComparison: () => void;
  knownCount: number;
  unknownCount: number;
}

export const ComparisonLab: React.FC<ComparisonLabProps> = ({
  comparisonData,
  isLoading,
  onRunComparison,
  knownCount,
  unknownCount,
}) => {
  if (!comparisonData && !isLoading) {
    return (
      <div className="glass-panel rounded-2xl p-8 border border-slate-800 text-center flex flex-col items-center justify-center gap-4">
        <GitCompare className="w-12 h-12 text-brand-400" />
        <div>
          <h3 className="text-base font-bold text-white">Comparative Evaluation Laboratory</h3>
          <p className="text-xs text-slate-400 max-w-lg mt-1">
            Compare Pawlak Rough Set Theory with 4 classical Machine Learning algorithms (Random Forest, Multinomial Naive Bayes, Logistic Regression, and Decision Tree) on the current symptom query ({knownCount} known, {unknownCount} unknown).
          </p>
        </div>
        <button
          onClick={onRunComparison}
          className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 text-white text-xs font-bold uppercase tracking-wider hover:from-brand-500 hover:to-indigo-500 transition-all shadow-lg shadow-brand-500/20 cursor-pointer"
        >
          Execute Multi-Model Comparison
        </button>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="glass-panel rounded-2xl p-8 border border-slate-800 text-center flex flex-col items-center justify-center gap-3">
        <div className="w-10 h-10 border-3 border-brand-500/30 border-t-brand-500 rounded-full animate-spin" />
        <p className="text-sm font-medium text-slate-300">
          Running Multi-Model Inference Across RST & ML Baselines...
        </p>
      </div>
    );
  }

  const rst = comparisonData?.rst_prediction;
  const mls = comparisonData?.ml_predictions || {};

  return (
    <div className="flex flex-col gap-6 animate-fadeIn">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-[11px] font-semibold text-brand-400 uppercase tracking-wider flex items-center gap-1.5">
            <GitCompare className="w-3.5 h-3.5" />
            Empirical Comparison Under Incomplete Symptoms
          </span>
          <h2 className="text-xl font-bold text-white mt-0.5">
            Rough Set Theory vs Supervised Machine Learning Baselines
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Current query has <strong className="text-white">{knownCount}</strong> known symptoms and{" "}
            <strong className="text-amber-400">{unknownCount}</strong> unknown symptoms (?).
          </p>
        </div>

        <button
          onClick={onRunComparison}
          className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors shrink-0 flex items-center gap-1.5 self-start sm:self-auto cursor-pointer"
        >
          <Clock className="w-3.5 h-3.5 text-brand-400" />
          <span>Re-evaluate Models ({comparisonData?.total_latency_ms} ms)</span>
        </button>
      </div>

      {/* Side-by-side Model Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Card 1: Rough Set Theory (Primary) */}
        {rst && (
          <div className="glass-panel rounded-2xl p-5 border-2 border-brand-500/50 bg-gradient-to-b from-brand-950/20 to-slate-900/60 shadow-xl flex flex-col justify-between gap-4 relative overflow-hidden">
            <div className="absolute top-2 right-2 px-2 py-0.5 rounded-full bg-brand-500/20 border border-brand-500/30 text-[10px] font-mono text-brand-300">
              PRIMARY ENGINE
            </div>
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Layers className="w-5 h-5 text-brand-400" />
                <h3 className="text-sm font-bold text-white">Rough Set Theory</h3>
              </div>
              <p className="text-[11px] text-slate-400 mb-3">
                Pawlak tolerance relation over complete reference profiles.
              </p>

              <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">
                  Top Recommended Disease
                </span>
                <span className="text-lg font-bold text-brand-400 block truncate">
                  {rst.primary_disease}
                </span>
                <div className="flex items-center justify-between text-xs font-mono mt-1">
                  <span className="text-slate-400">Rough Membership μ:</span>
                  <span className="text-white font-bold">{(rst.confidence * 100).toFixed(1)}%</span>
                </div>
              </div>

              <div className="mt-3 text-[11px] space-y-1.5 text-slate-300">
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Pawlak Status:</span>
                  <span className="font-mono text-emerald-400 font-semibold">{rst.approximation_status}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Tolerance Class [q]_T:</span>
                  <span className="font-mono text-white">{rst.tolerance_class_size} objects</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Latency:</span>
                  <span className="font-mono text-slate-400">{rst.latency_ms} ms</span>
                </div>
              </div>
            </div>

            <div className="p-2.5 rounded-xl bg-emerald-950/30 border border-emerald-800/40 text-[11px] text-emerald-300">
              <strong className="block text-[10px] uppercase font-bold text-emerald-400 mb-0.5">
                Incomplete Data Semantics:
              </strong>
              {rst.handling_of_unknowns}
            </div>
          </div>
        )}

        {/* Card 2: Random Forest */}
        {mls["RandomForest"] && (
          <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Cpu className="w-5 h-5 text-indigo-400" />
                <h3 className="text-sm font-bold text-white">Random Forest (100 Trees)</h3>
              </div>
              <p className="text-[11px] text-slate-400 mb-3">
                Ensemble bagging of 100 randomized decision trees.
              </p>

              <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">
                  Predicted Disease
                </span>
                <span className="text-lg font-bold text-white block truncate">
                  {mls["RandomForest"].predicted_disease}
                </span>
                <div className="flex items-center justify-between text-xs font-mono mt-1">
                  <span className="text-slate-400">Class Probability:</span>
                  <span className="text-indigo-400 font-bold">
                    {(mls["RandomForest"].confidence * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              {mls["RandomForest"].top_candidates.length > 1 && (
                <div className="mt-3 text-[11px] space-y-1">
                  <span className="text-[10px] text-slate-500 uppercase block font-semibold">Other Candidates:</span>
                  {mls["RandomForest"].top_candidates.slice(1, 3).map((c, i) => (
                    <div key={i} className="flex justify-between text-slate-300">
                      <span className="truncate max-w-[140px]">{c.disease}:</span>
                      <span className="font-mono text-slate-400">{(c.probability * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400">
              <strong className="block text-[10px] uppercase font-bold text-slate-500 mb-0.5">
                Incomplete Handling:
              </strong>
              {mls["RandomForest"].handling_of_unknowns}
            </div>
          </div>
        )}

        {/* Card 3: Bernoulli Naive Bayes */}
        {(mls["BernoulliNB"] || mls["MultinomialNB"]) && (() => {
          const nb = mls["BernoulliNB"] || mls["MultinomialNB"];
          return (
            <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Cpu className="w-5 h-5 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white">Bernoulli Naive Bayes</h3>
                </div>
                <p className="text-[11px] text-slate-400 mb-3">
                  Binary multivariate Bernoulli estimator (preferred for 0/1 symptoms).
                </p>

                <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider block">
                    Predicted Disease
                  </span>
                  <span className="text-lg font-bold text-white block truncate">
                    {nb.predicted_disease}
                  </span>
                  <div className="flex items-center justify-between text-xs font-mono mt-1">
                    <span className="text-slate-400">Class Probability:</span>
                    <span className="text-cyan-400 font-bold">
                      {(nb.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>

                {nb.top_candidates.length > 1 && (
                  <div className="mt-3 text-[11px] space-y-1">
                    <span className="text-[10px] text-slate-500 uppercase block font-semibold">Other Candidates:</span>
                    {nb.top_candidates.slice(1, 3).map((c, i) => (
                      <div key={i} className="flex justify-between text-slate-300">
                        <span className="truncate max-w-[140px]">{c.disease}:</span>
                        <span className="font-mono text-slate-400">{(c.probability * 100).toFixed(1)}%</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400">
                <strong className="block text-[10px] uppercase font-bold text-slate-500 mb-0.5">
                  Incomplete Handling:
                </strong>
                {nb.handling_of_unknowns}
              </div>
            </div>
          );
        })()}

        {/* Card 4: Logistic Regression */}
        {mls["LogisticRegression"] && (
          <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Cpu className="w-5 h-5 text-purple-400" />
                <h3 className="text-sm font-bold text-white">Logistic Regression</h3>
              </div>
              <p className="text-[11px] text-slate-400 mb-3">
                L2-regularized multinomial linear logit model.
              </p>

              <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">
                  Predicted Disease
                </span>
                <span className="text-lg font-bold text-white block truncate">
                  {mls["LogisticRegression"].predicted_disease}
                </span>
                <div className="flex items-center justify-between text-xs font-mono mt-1">
                  <span className="text-slate-400">Confidence:</span>
                  <span className="text-purple-400 font-bold">
                    {(mls["LogisticRegression"].confidence * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400">
              <strong className="block text-[10px] uppercase font-bold text-slate-500 mb-0.5">
                Incomplete Handling:
              </strong>
              {mls["LogisticRegression"].handling_of_unknowns}
            </div>
          </div>
        )}

        {/* Card 5: Decision Tree CART */}
        {mls["DecisionTree"] && (
          <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Cpu className="w-5 h-5 text-amber-400" />
                <h3 className="text-sm font-bold text-white">Decision Tree (CART)</h3>
              </div>
              <p className="text-[11px] text-slate-400 mb-3">
                Recursive axis-aligned partitioning tree.
              </p>

              <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">
                  Predicted Disease
                </span>
                <span className="text-lg font-bold text-white block truncate">
                  {mls["DecisionTree"].predicted_disease}
                </span>
                <div className="flex items-center justify-between text-xs font-mono mt-1">
                  <span className="text-slate-400">Leaf Purity:</span>
                  <span className="text-amber-400 font-bold">
                    {(mls["DecisionTree"].confidence * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400">
              <strong className="block text-[10px] uppercase font-bold text-slate-500 mb-0.5">
                Incomplete Handling:
              </strong>
              {mls["DecisionTree"].handling_of_unknowns}
            </div>
          </div>
        )}
      </div>

      {/* Critical Academic Discussion Note */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 bg-slate-900/40 text-xs text-slate-300 flex flex-col gap-2">
        <h4 className="font-bold text-white flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-brand-400" />
          Why Rough Set Theory Excels on Incomplete Medical Information
        </h4>
        <p className="text-slate-400 leading-relaxed">
          Standard statistical classifiers assume complete feature vectors and traditionally impute missing attributes with 0 (assuming the symptom is absent). If a patient actually has a symptom but did not mention it, treating it as 0 causes catastrophic path deviations in decision trees (dropping CART accuracy to 36.67% at 70% missing). In contrast, <strong>Rough Set Theory's tolerance relation [q]_T ignores unspecified attributes</strong>, searching for all compatible medical profiles and deriving deterministic Lower and Boundary approximations.
        </p>
      </div>
    </div>
  );
};

import React, { useState, useEffect } from "react";
import { GitCompare, Layers, Cpu, ShieldCheck, BarChart2, Info } from "lucide-react";
import type { CompareResponse, BenchmarksData } from "../types";
import { fetchBenchmarks } from "../api/client";

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
  const [benchmarksData, setBenchmarksData] = useState<BenchmarksData | null>(null);
  const [selectedMissingRate, setSelectedMissingRate] = useState<number>(0.0);

  useEffect(() => {
    async function loadBenchmarks() {
      try {
        const data = await fetchBenchmarks();
        setBenchmarksData(data);
      } catch (err) {
        console.error("Failed to load benchmarks:", err);
      }
    }
    loadBenchmarks();
  }, []);

  const summaryRows = benchmarksData?.comparison_summary || [];
  const selectedRow = summaryRows.find((r) => r.missing_rate === selectedMissingRate) || summaryRows[0];

  const rst = comparisonData?.rst_prediction;
  const mls = comparisonData?.ml_predictions || {};

  return (
    <div className="flex flex-col gap-5 animate-fadeIn">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-[11px] font-semibold text-brand-400 uppercase tracking-wider flex items-center gap-1.5">
            <GitCompare className="w-3.5 h-3.5" />
            Empirical Comparison Laboratory
          </span>
          <h2 className="text-xl font-bold text-white mt-0.5">
            Rough Set Theory vs Classical Machine Learning Baselines
          </h2>
          <p className="text-xs text-slate-300 mt-1 max-w-2xl">
            Comparing robustness under incomplete symptom information.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={onRunComparison}
            disabled={isLoading}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white text-xs font-bold transition-all shadow-md shadow-brand-500/20 disabled:opacity-50 cursor-pointer"
          >
            {isLoading ? "Running Models..." : "Evaluate Current Symptoms"}
          </button>
        </div>
      </div>

      {/* Methodology Note */}
      <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300 flex items-center gap-2.5">
        <Info className="w-4 h-4 text-brand-400 shrink-0" />
        <span>ML baseline: unknown symptoms are zero-imputed; RST does not impute unknown symptoms.</span>
      </div>

      {/* SECTION 1: Interactive Benchmark Switcher Across Missing Rates */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <BarChart2 className="w-4 h-4 text-brand-400" />
            <h3 className="text-sm font-bold text-white">
              Verified Benchmark Accuracies Across Missing Symptom Rates
            </h3>
          </div>

          {/* Missing Rate Selector Pills */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-xs text-slate-400 font-semibold mr-1">Switch Rate:</span>
            {[
              { rate: 0.0, label: "Complete (0%)" },
              { rate: 0.1, label: "10% Missing" },
              { rate: 0.3, label: "30% Missing" },
              { rate: 0.5, label: "50% Missing" },
              { rate: 0.7, label: "70% Missing" },
            ].map(({ rate, label }) => (
              <button
                key={rate}
                onClick={() => setSelectedMissingRate(rate)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                  selectedMissingRate === rate
                    ? "bg-brand-500 text-white shadow-md shadow-brand-500/20"
                    : "bg-slate-900 text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* 5-Model Benchmark Cards for the Selected Missing Rate */}
        {selectedRow && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            {/* Model 1: Rough Set Top-1 */}
            <div className="p-4 rounded-xl bg-slate-900/90 border border-brand-500/40 flex flex-col justify-between gap-2 shadow-sm">
              <div>
                <span className="text-[10px] text-brand-400 uppercase font-bold tracking-wider block">
                  Primary Research Method
                </span>
                <strong className="text-sm text-white block mt-0.5">Rough Set Theory</strong>
                <span className="text-[11px] text-slate-400 block mt-1">Tolerance neighborhood over known attributes</span>
              </div>
              <div className="pt-2 border-t border-slate-800/80">
                <div className="text-2xl font-black text-brand-400 font-mono">
                  {(selectedRow.RST_accuracy * 100).toFixed(2)}%
                </div>
                <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                  Top-3: <strong className="text-cyan-400">{(selectedRow.RST_top3_accuracy * 100).toFixed(2)}%</strong>
                </div>
              </div>
            </div>

            {/* Model 2: Bernoulli Naive Bayes */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between gap-2">
              <div>
                <span className="text-[10px] text-cyan-400 uppercase font-bold tracking-wider block">
                  ML Baseline 1
                </span>
                <strong className="text-sm text-white block mt-0.5">Bernoulli Naive Bayes</strong>
                <span className="text-[11px] text-slate-400 block mt-1">Binary multivariate likelihood</span>
              </div>
              <div className="pt-2 border-t border-slate-800/80">
                <div className="text-2xl font-black text-slate-200 font-mono">
                  {(((selectedRow.BernoulliNB_accuracy ?? selectedRow.MultinomialNB_accuracy ?? 0) * 100)).toFixed(2)}%
                </div>
                <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                  Degradation: {(((selectedRow.BernoulliNB_accuracy ?? selectedRow.MultinomialNB_accuracy ?? 1) - 1) * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Model 3: Logistic Regression */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between gap-2">
              <div>
                <span className="text-[10px] text-purple-400 uppercase font-bold tracking-wider block">
                  ML Baseline 2
                </span>
                <strong className="text-sm text-white block mt-0.5">Logistic Regression</strong>
                <span className="text-[11px] text-slate-400 block mt-1">Multinomial logistic regression</span>
              </div>
              <div className="pt-2 border-t border-slate-800/80">
                <div className="text-2xl font-black text-slate-200 font-mono">
                  {(selectedRow.LogisticRegression_accuracy * 100).toFixed(2)}%
                </div>
                <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                  Degradation: {((selectedRow.LogisticRegression_accuracy - 1.0) * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Model 4: Random Forest */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between gap-2">
              <div>
                <span className="text-[10px] text-indigo-400 uppercase font-bold tracking-wider block">
                  ML Baseline 3
                </span>
                <strong className="text-sm text-white block mt-0.5">Random Forest</strong>
                <span className="text-[11px] text-slate-400 block mt-1">Random forest ensemble (100 trees)</span>
              </div>
              <div className="pt-2 border-t border-slate-800/80">
                <div className="text-2xl font-black text-slate-200 font-mono">
                  {(selectedRow.RandomForest_accuracy * 100).toFixed(2)}%
                </div>
                <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                  Degradation: {((selectedRow.RandomForest_accuracy - 0.9762) * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Model 5: Decision Tree */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-rose-900/40 flex flex-col justify-between gap-2">
              <div>
                <span className="text-[10px] text-rose-400 uppercase font-bold tracking-wider block">
                  ML Baseline 4
                </span>
                <strong className="text-sm text-white block mt-0.5">Decision Tree</strong>
                <span className="text-[11px] text-slate-400 block mt-1">Decision tree classification</span>
              </div>
              <div className="pt-2 border-t border-slate-800/80">
                <div className="text-2xl font-black text-rose-400 font-mono">
                  {(selectedRow.DecisionTree_accuracy * 100).toFixed(2)}%
                </div>
                <div className="text-[10px] text-rose-400/80 font-mono mt-0.5">
                  Degradation: {((selectedRow.DecisionTree_accuracy - 0.9762) * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="text-[11px] text-slate-400 pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-1 border-t border-slate-800/60">
          <span>Evaluated on 42 held-out test samples across 5 missing symptom levels</span>
          <span className="text-slate-300">RST preserves unknown symptoms as unknown rather than treating them as absent.</span>
        </div>
      </div>

      {/* SECTION 2: Active User Query Real-time Multi-Model Comparison */}
      {comparisonData && (
        <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col gap-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Cpu className="w-4 h-4 text-brand-400" />
              Live Predictions on Active Symptom Query ({knownCount} Known, {unknownCount} Unknown)
            </h3>
            <span className="text-xs font-mono text-slate-400">
              Total Latency: {comparisonData.total_latency_ms} ms
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* Card 1: Rough Set Recommender */}
            {rst && (
              <div className="glass-panel rounded-2xl p-5 border border-brand-500/40 flex flex-col justify-between gap-4 shadow-xl">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Layers className="w-5 h-5 text-brand-400" />
                    <h4 className="text-sm font-bold text-white">Rough Set Recommender</h4>
                  </div>
                  <p className="text-[11px] text-slate-400 mb-3">
                    Tolerance neighborhood [q]ᴛ derived without zero-imputation.
                  </p>

                  <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                      Recommended Disease
                    </span>
                    <span className="text-base font-bold text-brand-300 block truncate mt-0.5">
                      {rst.primary_disease}
                    </span>
                    <div className="flex items-center justify-between text-xs font-mono mt-1">
                      <span className="text-slate-400">Rough Membership Degree:</span>
                      <span className="text-brand-400 font-bold">μ(q) = {rst.confidence.toFixed(4)}</span>
                    </div>
                  </div>

                  <div className="mt-3 text-[11px] text-slate-400 font-mono">
                    Tolerance Support: <strong className="text-white">{rst.tolerance_class_size}</strong> objects
                  </div>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400">
                  <strong className="block text-[10px] uppercase font-bold text-slate-400 mb-0.5">
                    Approximation Status:
                  </strong>
                  <span className="text-brand-300">{rst.approximation_status}</span>
                </div>
              </div>
            )}

            {/* Card 2: Bernoulli Naive Bayes */}
            {mls["BernoulliNB"] && (
              <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Cpu className="w-5 h-5 text-cyan-400" />
                    <h4 className="text-sm font-bold text-white">Bernoulli Naive Bayes</h4>
                  </div>
                  <p className="text-[11px] text-slate-400 mb-3">
                    Binary multivariate likelihood.
                  </p>

                  <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                      Predicted Disease
                    </span>
                    <span className="text-base font-bold text-white block truncate mt-0.5">
                      {mls["BernoulliNB"].predicted_disease}
                    </span>
                    <div className="flex items-center justify-between text-xs font-mono mt-1">
                      <span className="text-slate-400">Posterior Prob:</span>
                      <span className="text-cyan-400 font-bold">
                        {(mls["BernoulliNB"].confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400">
                  <strong className="block text-[10px] uppercase font-bold text-slate-400 mb-0.5">
                    Incomplete Handling:
                  </strong>
                  <span className="text-slate-300">Zero-imputed</span>
                </div>
              </div>
            )}

            {/* Card 3: Logistic Regression */}
            {mls["LogisticRegression"] && (
              <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Cpu className="w-5 h-5 text-purple-400" />
                    <h4 className="text-sm font-bold text-white">Logistic Regression</h4>
                  </div>
                  <p className="text-[11px] text-slate-400 mb-3">
                    Multinomial logistic regression.
                  </p>

                  <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                      Predicted Disease
                    </span>
                    <span className="text-base font-bold text-white block truncate mt-0.5">
                      {mls["LogisticRegression"].predicted_disease}
                    </span>
                    <div className="flex items-center justify-between text-xs font-mono mt-1">
                      <span className="text-slate-400">Softmax Prob:</span>
                      <span className="text-purple-400 font-bold">
                        {(mls["LogisticRegression"].confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400">
                  <strong className="block text-[10px] uppercase font-bold text-slate-400 mb-0.5">
                    Incomplete Handling:
                  </strong>
                  <span className="text-slate-300">Zero-imputed</span>
                </div>
              </div>
            )}

            {/* Card 4: Random Forest */}
            {mls["RandomForest"] && (
              <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Cpu className="w-5 h-5 text-indigo-400" />
                    <h4 className="text-sm font-bold text-white">Random Forest</h4>
                  </div>
                  <p className="text-[11px] text-slate-400 mb-3">
                    Random forest ensemble.
                  </p>

                  <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                      Predicted Disease
                    </span>
                    <span className="text-base font-bold text-white block truncate mt-0.5">
                      {mls["RandomForest"].predicted_disease}
                    </span>
                    <div className="flex items-center justify-between text-xs font-mono mt-1">
                      <span className="text-slate-400">Ensemble Vote:</span>
                      <span className="text-indigo-400 font-bold">
                        {(mls["RandomForest"].confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400">
                  <strong className="block text-[10px] uppercase font-bold text-slate-400 mb-0.5">
                    Incomplete Handling:
                  </strong>
                  <span className="text-slate-300">Zero-imputed</span>
                </div>
              </div>
            )}

            {/* Card 5: Decision Tree */}
            {mls["DecisionTree"] && (
              <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Cpu className="w-5 h-5 text-rose-400" />
                    <h4 className="text-sm font-bold text-white">Decision Tree</h4>
                  </div>
                  <p className="text-[11px] text-slate-400 mb-3">
                    Single decision tree.
                  </p>

                  <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                      Predicted Disease
                    </span>
                    <span className="text-base font-bold text-white block truncate mt-0.5">
                      {mls["DecisionTree"].predicted_disease}
                    </span>
                    <div className="flex items-center justify-between text-xs font-mono mt-1">
                      <span className="text-slate-400">Leaf Purity:</span>
                      <span className="text-rose-400 font-bold">
                        {(mls["DecisionTree"].confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400">
                  <strong className="block text-[10px] uppercase font-bold text-slate-400 mb-0.5">
                    Incomplete Handling:
                  </strong>
                  <span className="text-slate-300">Zero-imputed</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Academic Discussion Note */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 bg-slate-900/40 text-xs text-slate-300 flex flex-col gap-2">
        <h4 className="font-bold text-white flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-brand-400" />
          Methodological Principle: Unknown Symptom ≠ Absent Symptom
        </h4>
        <p className="text-slate-300 leading-relaxed">
          Standard statistical classifiers assume complete feature vectors and traditionally impute missing attributes with 0 (assuming the symptom is absent). If a patient actually has a symptom but did not report it, forcing ? → 0 causes performance degradation in greedy tree splits (dropping Decision Tree accuracy from 97.62% down to 36.67% at 70% missing). In contrast, <strong>Rough Set Theory's tolerance relation T(q, x) strictly ignores unspecified attributes</strong>, searching for all compatible training profiles—RST preserves unknown symptoms as unknown rather than treating them as absent.
        </p>
      </div>
    </div>
  );
};

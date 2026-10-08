import React, { useState, useEffect } from "react";
import { BookOpen, Search, ArrowRight, Info } from "lucide-react";
import type { AssociationRule } from "../types";
import { fetchAssociationRules, fetchDiseases } from "../api/client";

export const AssociationRulesExplorer: React.FC = () => {
  const [rules, setRules] = useState<AssociationRule[]>([]);
  const [diseases, setDiseases] = useState<string[]>([]);
  const [selectedDisease, setSelectedDisease] = useState<string>("");
  const [minConfidence, setMinConfidence] = useState<number>(0.8);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [displayLimit, setDisplayLimit] = useState<number>(100);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [rulesRes, diseasesRes] = await Promise.all([
          fetchAssociationRules(selectedDisease || undefined, minConfidence, displayLimit),
          fetchDiseases(),
        ]);
        setRules(rulesRes.rules);
        setDiseases(diseasesRes.diseases);
      } catch (err) {
        console.error("Error fetching rules:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [selectedDisease, minConfidence, displayLimit]);

  const filteredRules = rules.filter((r) => {
    const text = (r.antecedents.join(" ") + " " + r.consequent).toLowerCase();
    return text.includes(searchTerm.toLowerCase());
  });

  return (
    <div className="flex flex-col gap-5 animate-fadeIn">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800">
        <span className="text-[11px] font-semibold text-brand-400 uppercase tracking-wider flex items-center gap-1.5">
          <BookOpen className="w-3.5 h-3.5" />
          Rule-Based Reasoning Support
        </span>
        <h2 className="text-xl font-bold text-white mt-0.5">
          Association Rules Explorer (Apriori Mining)
        </h2>
        <p className="text-xs text-slate-300 mt-1 max-w-3xl">
          Mined frequent itemsets connecting multi-symptom combinations to disease prognoses. Provides transparent IF-THEN rules with statistical support, confidence, and lift.
        </p>

        {/* Concise Metric Legend */}
        <div className="mt-3 pt-3 border-t border-slate-800/80 flex flex-wrap items-center gap-4 text-[11px] text-slate-400">
          <div className="flex items-center gap-1.5">
            <Info className="w-3.5 h-3.5 text-brand-400 shrink-0" />
            <span><strong>Support:</strong> Frequency of co-occurrence in training records</span>
          </div>
          <div>
            <span><strong>Confidence:</strong> Conditional likelihood P(Disease | Symptoms)</span>
          </div>
          <div>
            <span><strong>Lift:</strong> Ratio over baseline prevalence (&gt; 1.0 indicates strong association)</span>
          </div>
        </div>
      </div>

      {/* Filter Controls: Stacks cleanly on mobile (Search -> Disease -> Confidence), horizontal on desktop */}
      <div className="glass-panel rounded-2xl p-4 border border-slate-800 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        {/* Search */}
        <div className="relative flex-1 md:max-w-xs lg:max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search symptoms or disease in rules..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-brand-500"
          />
        </div>

        {/* Filter Controls: Stack on mobile (< sm), inline on tablet/desktop */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          {/* Disease Dropdown */}
          <select
            value={selectedDisease}
            onChange={(e) => setSelectedDisease(e.target.value)}
            className="bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-brand-500 w-full sm:w-auto"
          >
            <option value="">All 41 Diseases</option>
            {diseases.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>

          {/* Confidence Slider: Stacks cleanly on mobile without clipping */}
          <div className="flex items-center justify-between sm:justify-start gap-2.5 bg-slate-900 px-3.5 py-2 rounded-xl border border-slate-800 text-xs">
            <span className="text-slate-400 text-[11px] whitespace-nowrap font-medium">
              Display confidence ≥ {(minConfidence * 100).toFixed(0)}%
            </span>
            <input
              type="range"
              min="0.5"
              max="1.0"
              step="0.05"
              value={minConfidence}
              onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
              className="w-24 sm:w-20 accent-brand-500 cursor-pointer"
              aria-label="Display confidence threshold"
            />
          </div>
        </div>
      </div>

      {/* Rules List */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
          <span className="text-xs font-bold text-slate-300">
            Showing {Math.min(filteredRules.length, displayLimit)} of 831 Association Rules
          </span>
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400 bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800">
            <span className="text-slate-300 font-medium">Mining configuration · min confidence = 0.70</span>
            <span className="font-mono text-slate-400">· min_support = 0.01</span>
          </div>
        </div>

        {loading ? (
          <div className="py-12 text-center text-xs text-slate-400">Loading rules...</div>
        ) : filteredRules.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-400">No matching rules found.</div>
        ) : (
          <div className="flex flex-col gap-3">
            <div className="flex flex-col gap-2.5 max-h-[520px] overflow-y-auto pr-1">
              {filteredRules.slice(0, displayLimit).map((rule, idx) => (
                <div
                  key={idx}
                  className="bg-slate-900/70 p-3.5 rounded-xl border border-slate-800/80 hover:border-slate-700 transition-all flex flex-col md:flex-row md:items-center justify-between gap-3"
                >
                  {/* Antecedent -> Consequent */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      IF
                    </span>
                    {rule.antecedents.map((ant) => (
                      <span
                        key={ant}
                        className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200 text-xs font-mono border border-slate-700/60"
                      >
                        {ant.replace(/_/g, " ")}
                      </span>
                    ))}
                    <ArrowRight className="w-4 h-4 text-brand-400 shrink-0 mx-1" />
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      THEN
                    </span>
                    <span className="text-sm font-bold text-white bg-brand-950/60 px-3 py-1 rounded-lg border border-brand-800/60">
                      {rule.consequent}
                    </span>
                  </div>

                  {/* Metrics Badges */}
                  <div className="flex items-center gap-4 text-xs font-mono shrink-0">
                    <div>
                      <span className="text-slate-400 text-[10px] block uppercase">Confidence</span>
                      <span className="text-brand-400 font-bold">
                        {(rule.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400 text-[10px] block uppercase">Lift</span>
                      <span className="text-emerald-400 font-bold">{rule.lift.toFixed(1)}x</span>
                    </div>
                    <div>
                      <span className="text-slate-400 text-[10px] block uppercase">Support</span>
                      <span className="text-slate-300">{(rule.support * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {rules.length >= displayLimit && displayLimit < 831 && (
              <div className="flex justify-center pt-2">
                <button
                  onClick={() => setDisplayLimit((prev) => Math.min(prev + 100, 831))}
                  className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-xs text-brand-400 font-semibold border border-slate-800 transition-all cursor-pointer"
                >
                  Load Next 100 Rules
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

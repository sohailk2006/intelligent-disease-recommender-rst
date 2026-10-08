import React, { useState, useEffect } from "react";
import { Layers, ShieldCheck, Award, Info } from "lucide-react";
import type { ReductsData, SystemMetadata } from "../types";
import { fetchReducts, fetchMetadata } from "../api/client";

export const RstTheoryExplorer: React.FC = () => {
  const [reductsData, setReductsData] = useState<ReductsData | null>(null);
  const [metadata, setMetadata] = useState<SystemMetadata | null>(null);
  const [selectedReductId, setSelectedReductId] = useState<string>("reduct_johnson");
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function load() {
      try {
        const [r, m] = await Promise.all([fetchReducts(), fetchMetadata()]);
        setReductsData(r);
        setMetadata(m);
      } catch (err) {
        console.error("Error fetching RST theory data:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="glass-panel rounded-2xl p-8 border border-slate-800 text-center flex flex-col items-center justify-center gap-3">
        <div className="w-10 h-10 border-3 border-brand-500/30 border-t-brand-500 rounded-full animate-spin" />
        <p className="text-sm font-medium text-slate-300">Loading Rough Set Formal Theory & Reducts...</p>
      </div>
    );
  }

  const activeReduct = reductsData?.reducts.find((r) => r.id === selectedReductId) || reductsData?.reducts[0];

  return (
    <div className="flex flex-col gap-6 animate-fadeIn">
      {/* Title Card */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800">
        <span className="text-[11px] font-semibold text-brand-400 uppercase tracking-wider flex items-center gap-1.5">
          <Layers className="w-3.5 h-3.5" />
          Mathematical Foundations & Reduct Discovery
        </span>
        <h2 className="text-xl font-bold text-white mt-0.5">
          Pawlak Rough Set Theory (RST) Formalism
        </h2>
        <p className="text-xs text-slate-300 mt-1 max-w-3xl">
          Computed directly from the full training decision table.
        </p>
      </div>

      {/* Pawlak Theory Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel rounded-2xl p-4 border border-slate-800 flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-bold text-white mt-1">Decision Table DT</h4>
            <div className="text-xl font-extrabold text-brand-400 font-mono mt-2">|U| = 4,920</div>
            <p className="text-[11px] text-slate-400 mt-1">
              Condition attributes |C| = 132, Decision classes |D| = 41 (120 records per class, perfectly balanced).
            </p>
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-4 border border-slate-800 flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-bold text-white mt-1">Indiscernibility IND(C)</h4>
            <div className="text-xl font-extrabold text-emerald-400 font-mono mt-2">304 Patterns</div>
            <p className="text-[11px] text-slate-400 mt-1">
              The 4,920 records partition into exactly 304 unique symptom profiles with zero contradictions.
            </p>
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-4 border border-slate-800 flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-bold text-white mt-1">Degree of Dependency γ</h4>
            <div className="text-xl font-extrabold text-cyan-400 font-mono mt-2">γ_C(D) = 1.0</div>
            <p className="text-[11px] text-slate-400 mt-1">
              Positive region POS_C(D) covers 100% of the universe. Decisions completely depend on conditions.
            </p>
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-4 border border-slate-800 flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-bold text-white mt-1">Discernibility & Core</h4>
            <div className="text-xl font-extrabold text-amber-400 font-mono mt-2">|CORE(C)| = 0</div>
            <p className="text-[11px] text-slate-400 mt-1">
              Every distinct disease pair differs by at least 2 attributes (min clause = 2). Multiple minimal reducts exist!
            </p>
          </div>
        </div>
      </div>

      {/* Reduct Selector & Analysis */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Award className="w-5 h-5 text-brand-400" />
              Inclusion-Minimal Reduct Candidates
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Attribute subsets preserving 100% classification dependency (γ = 1.0). No redundant attributes within this candidate under the tested criterion.
            </p>
          </div>

          <div className="flex items-center gap-2">
            {reductsData?.reducts.map((r) => (
              <button
                key={r.id}
                onClick={() => setSelectedReductId(r.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                  selectedReductId === r.id
                    ? "bg-brand-500 text-white font-bold shadow-md shadow-brand-500/20"
                    : "bg-slate-900 text-slate-400 hover:bg-slate-800 hover:text-white border border-slate-800"
                }`}
              >
                {r.name.split(" ")[0]} ({r.size} attrs)
              </button>
            ))}
          </div>
        </div>

        {activeReduct && (
          <div className="mt-5 flex flex-col gap-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Reduct Size</span>
                <span className="text-2xl font-bold text-white font-mono">{activeReduct.size}</span>
                <span className="text-[10px] text-emerald-400 block mt-0.5">
                  Reduced from 132 symptoms ({(100 - (activeReduct.size / 132) * 100).toFixed(0)}% reduction)
                </span>
              </div>

              <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Dependency Preserved</span>
                <span className="text-2xl font-bold text-brand-400 font-mono">
                  γ_R(D) = {activeReduct.dependency_degree.toFixed(2)}
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">
                  100% consistency on all 4,920 records
                </span>
              </div>

              <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Minimality Axiom</span>
                <span className="text-sm font-bold text-emerald-400 block mt-1 flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4" />
                  Inclusion-Minimal Reduct
                </span>
                <span className="text-[10px] text-slate-400 block mt-0.5">
                  ∀a ∈ R: γ_(R\a)(D) &lt; 1.0 (No redundant attributes within this candidate under the tested criterion)
                </span>
              </div>
            </div>

            {/* Reduct Attributes Tag Cloud - all 38 attributes visible */}
            <div>
              <span className="text-xs font-semibold text-slate-300 block mb-2">
                {activeReduct.size} Selected Reduct Attributes
              </span>
              <div className="flex flex-wrap gap-2 p-1">
                {activeReduct.attributes.map((attr, index) => (
                  <span
                    key={attr}
                    className="px-2.5 py-1 rounded-lg bg-slate-900 text-slate-200 border border-slate-700/80 text-xs font-mono flex items-center gap-1.5"
                  >
                    <span className="text-[10px] text-brand-400 font-bold">#{index + 1}</span>
                    <span>{attr.replace(/_/g, " ")}</span>
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Skowron Discernibility Matrix Overview */}
      {metadata?.discernibility_summary && (
        <div className="glass-panel rounded-2xl p-5 border border-slate-800 text-xs text-slate-400 flex flex-col gap-2">
          <h4 className="text-sm font-bold text-white flex items-center gap-2">
            <Info className="w-4 h-4 text-brand-400" />
            Skowron's Discernibility Matrix & Boolean Simplification
          </h4>
          <p className="leading-relaxed">
            The discernibility matrix M = (c_ij) evaluated <strong>{metadata.discernibility_summary.total_discerning_pairs}</strong> distinct object pairs with differing disease diagnoses. It yielded <strong>{metadata.discernibility_summary.unique_discernibility_clauses}</strong> unique Boolean discernibility clauses with an average clause length of <strong>{metadata.discernibility_summary.avg_clause_size}</strong> symptoms.
          </p>
        </div>
      )}
    </div>
  );
};

import React, { useState } from "react";
import {
  CheckCircle,
  Info,
  Clock,
  Layers,
  HelpCircle,
  TrendingUp,
  FileText,
  ArrowRight,
  ShieldCheck,
  Split,
  ChevronDown,
  ChevronUp,
  AlertCircle,
} from "lucide-react";
import type { RecommendResponse } from "../types";

interface RecommendationViewProps {
  result: RecommendResponse | null;
  isLoading: boolean;
  onExploreComparison?: () => void;
}

export const RecommendationView: React.FC<RecommendationViewProps> = ({
  result,
  isLoading,
  onExploreComparison,
}) => {
  const [isReasoningExpanded, setIsReasoningExpanded] = useState<boolean>(true);

  if (isLoading) {
    return (
      <div className="glass-panel rounded-2xl p-8 border border-slate-800 text-center flex flex-col items-center justify-center gap-3">
        <div className="w-10 h-10 border-3 border-brand-500/30 border-t-brand-500 rounded-full animate-spin" />
        <p className="text-sm font-medium text-slate-300">
          Computing Rough Set Tolerance Classes & Approximations...
        </p>
        <p className="text-xs text-slate-500">
          Comparing known attributes against 4,920 records without zero-imputation
        </p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="glass-panel rounded-2xl p-8 border border-slate-800 text-center flex flex-col items-center justify-center gap-3 text-slate-400">
        <Layers className="w-10 h-10 text-slate-600" />
        <h3 className="text-sm font-semibold text-slate-300">No Active Recommendation</h3>
        <p className="text-xs max-w-md text-slate-500">
          Select symptom attributes above or click one of the clinical presets (e.g. Dengue, Malaria, Diabetes) and click "Analyze Symptoms".
        </p>
      </div>
    );
  }

  const primary = result.primary_recommendation;
  const reasoning = result.rough_set_reasoning;
  const candidates = result.top_candidates;
  const rules = result.matched_association_rules;

  // Determine Certainty State
  const isInsufficientInfo = reasoning.known_symptoms_count === 0 || reasoning.tolerance_class_size === 0 || !primary;
  const isCertain = primary?.approximation_code === "LOWER" && !reasoning.boundary_uncertainty;

  // Approximation Badge styling
  const getApproxBadge = (code: string) => {
    switch (code) {
      case "LOWER":
        return {
          bg: "bg-emerald-500/15 border-emerald-500/30 text-emerald-400",
          icon: ShieldCheck,
          label: "Lower Approximation under selected tolerance relation T_*(X) — Deterministic Certainty",
          desc: "The query's tolerance neighborhood [q]_T is a strict subset of this disease class. All matching reference objects belong exclusively to this condition.",
        };
      case "BOUNDARY":
        return {
          bg: "bg-amber-500/15 border-amber-500/30 text-amber-400",
          icon: Split,
          label: "Boundary Region under selected tolerance relation BN_T(X) — Incomplete Information Ambiguity",
          desc: "The query matches training objects across multiple disease classes due to unknown ('?') symptoms. Discernibility is incomplete.",
        };
      default:
        return {
          bg: "bg-indigo-500/15 border-indigo-500/30 text-indigo-400",
          icon: Info,
          label: "Upper Approximation under selected tolerance relation T^*(X) — Plausible Candidate",
          desc: "Non-empty intersection between query tolerance neighborhood and this disease class.",
        };
    }
  };

  const primaryBadge = primary ? getApproxBadge(primary.approximation_code) : null;

  return (
    <div className="flex flex-col gap-6 animate-fadeIn">
      {/* STATE 1: Insufficient Information State */}
      {isInsufficientInfo ? (
        <div className="glass-panel rounded-2xl p-6 border border-amber-800/60 bg-amber-950/20 flex flex-col gap-3">
          <div className="flex items-center gap-2 text-amber-400">
            <AlertCircle className="w-5 h-5" />
            <h3 className="text-base font-bold">
              Insufficient Information: All 132 Symptoms Unspecified
            </h3>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Because no symptoms were specified as present (1) or absent (0), the query's compatibility/tolerance neighborhood <code className="text-amber-300 font-mono">[q]_T</code> spans the entire universe ($N = 4,920$). Every disease class shares an identical uniform baseline rough membership degree ($\mu = 120 / 4920 = 2.44\%$).
          </p>
          <p className="text-xs text-amber-200/80">
            <strong>Action Required:</strong> Please specify at least 1-2 positive or negative symptoms using the console above, or click any of the <strong>Clinical Presets</strong> to evaluate live disease reasoning.
          </p>
        </div>
      ) : (
        /* STATE 2 & 3: Certain Recommendation OR Candidate Recommendations (Ambiguous) */
        <div
          className={`glass-panel rounded-2xl p-6 border relative overflow-hidden shadow-2xl ${
            isCertain
              ? "border-emerald-500/40 bg-slate-900/40"
              : "border-amber-500/40 bg-slate-900/40"
          }`}
        >
          <div className="absolute top-0 right-0 w-80 h-80 bg-brand-500/5 rounded-full blur-3xl pointer-events-none" />

          {/* Header Row */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
            <div>
              <span
                className={`text-[11px] font-semibold tracking-wider uppercase flex items-center gap-1.5 ${
                  isCertain ? "text-emerald-400" : "text-amber-400"
                }`}
              >
                {isCertain ? (
                  <>
                    <ShieldCheck className="w-3.5 h-3.5" />
                    Certain Recommendation (Lower Approximation)
                  </>
                ) : (
                  <>
                    <Split className="w-3.5 h-3.5" />
                    Candidate Recommendations (Boundary Uncertainty — {candidates.length} Possible Diseases)
                  </>
                )}
              </span>

              <h2 className="text-2xl sm:text-3xl font-extrabold text-white mt-1 flex items-center gap-2">
                {primary?.disease}
                {!isCertain && (
                  <span className="text-xs font-mono font-normal px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800">
                    Lead Candidate
                  </span>
                )}
              </h2>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-right">
                <div
                  className={`text-2xl font-black font-mono ${
                    isCertain ? "text-emerald-400" : "text-amber-400"
                  }`}
                >
                  {primary?.confidence_percentage}%
                </div>
                <div className="text-[10px] text-slate-400 font-mono">
                  Rough Membership μ(q) = {primary?.membership_degree}
                </div>
              </div>

              <div className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400 font-mono flex items-center gap-1">
                <Clock className="w-3 h-3 text-brand-400" />
                <span>{result.prediction_latency_ms} ms</span>
              </div>
            </div>
          </div>

          {/* Approximation Status Alert */}
          {primaryBadge && (
            <div className={`mt-4 p-3.5 rounded-xl border flex items-start gap-3 ${primaryBadge.bg}`}>
              <primaryBadge.icon className="w-5 h-5 shrink-0 mt-0.5" />
              <div>
                <div className="text-xs font-bold">{primaryBadge.label}</div>
                <div className="text-[11px] mt-0.5 opacity-90">{primaryBadge.desc}</div>
              </div>
            </div>
          )}

          {/* Quantitative Evidence Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
            <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                Tolerance Neighborhood [q]_T
              </span>
              <span className="text-lg font-bold text-white font-mono">
                {reasoning.tolerance_class_size} objects
              </span>
              <span className="text-[10px] text-emerald-400 block mt-0.5">
                {reasoning.is_exact_match ? "Exact compatibility" : "Maximal similarity"}
              </span>
            </div>

            <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                Known Symptoms
              </span>
              <span className="text-lg font-bold text-white font-mono">
                {reasoning.known_symptoms_count} / 132
              </span>
              <span className="text-[10px] text-slate-400 block mt-0.5">
                Evaluated in query
              </span>
            </div>

            <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                Unknown Symptoms (?)
              </span>
              <span className="text-lg font-bold text-amber-400 font-mono">
                {reasoning.unknown_symptoms_count}
              </span>
              <span className="text-[10px] text-slate-400 block mt-0.5">
                Ignored (never zero)
              </span>
            </div>

            <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                Reduct Overlap
              </span>
              <span className="text-lg font-bold text-brand-400 font-mono">
                {reasoning.reduct_alignment
                  ? `${reasoning.reduct_alignment.known_reduct_attributes_count} / ${reasoning.reduct_alignment.active_reduct_size}`
                  : "N/A"}
              </span>
              <span className="text-[10px] text-slate-400 block mt-0.5">
                {reasoning.reduct_alignment
                  ? `${(reasoning.reduct_alignment.coverage_ratio * 100).toFixed(0)}% minimal reduct`
                  : "Attributes"}
              </span>
            </div>
          </div>

          {/* Qualitative Evidence: Aligned Symptoms & Reduct Attributes */}
          <div className="mt-4 pt-4 border-t border-slate-800/80 flex flex-col gap-3">
            <div>
              <span className="text-xs font-semibold text-slate-300 block mb-1.5">
                Diagnostic Evidence: Aligned Present Symptoms for {primary?.disease}
              </span>
              {primary?.aligned_symptoms && primary.aligned_symptoms.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {primary.aligned_symptoms.map((s) => (
                    <span
                      key={s}
                      className="px-2.5 py-1 rounded-md bg-emerald-950/60 border border-emerald-800/60 text-emerald-300 text-xs font-medium flex items-center gap-1"
                    >
                      <CheckCircle className="w-3 h-3 text-emerald-400" />
                      {s.replace(/_/g, " ")}
                    </span>
                  ))}
                </div>
              ) : (
                <span className="text-xs text-slate-500 italic">
                  No positive symptoms explicitly aligned; matched via absence profile.
                </span>
              )}
            </div>

            {/* Reduct Attributes Active in Query */}
            {reasoning.reduct_alignment && reasoning.reduct_alignment.known_reduct_attributes.length > 0 && (
              <div>
                <span className="text-xs font-semibold text-slate-300 block mb-1.5">
                  Minimal Reduct Symptoms Active in Patient Query:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {reasoning.reduct_alignment.known_reduct_attributes.map((attr) => (
                    <span
                      key={attr}
                      className="px-2 py-0.5 rounded bg-brand-950/50 border border-brand-800/50 text-brand-300 text-[11px] font-mono"
                    >
                      {attr.replace(/_/g, " ")}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* SECTION 4: Expandable "How the System Reasoned" Pipeline */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <button
          onClick={() => setIsReasoningExpanded(!isReasoningExpanded)}
          className="w-full p-4 bg-slate-900/60 hover:bg-slate-900/90 transition-colors flex items-center justify-between text-left cursor-pointer"
        >
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-brand-400" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              How the System Reasoned (RST Tolerance Pipeline)
            </h4>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span>{isReasoningExpanded ? "Collapse" : "Expand"} Explanation</span>
            {isReasoningExpanded ? (
              <ChevronUp className="w-4 h-4 text-slate-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-slate-400" />
            )}
          </div>
        </button>

        {isReasoningExpanded && (
          <div className="p-5 flex flex-col gap-4 border-t border-slate-800/80 bg-slate-950/50">
            {/* Visual Flowchart */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              {/* Step 1 */}
              <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col justify-between gap-2">
                <div>
                  <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono mb-1">
                    <span>STEP 1</span>
                    <span className="text-brand-400 font-bold">{reasoning.known_symptoms_count} attrs</span>
                  </div>
                  <strong className="text-xs text-white block">Known Symptoms Ingested</strong>
                  <p className="text-[11px] text-slate-400 mt-1 leading-snug">
                    Query symptoms partitioned into known attributes (values 0 or 1) and unknown (?). Unknown symptoms are preserved without penalty.
                  </p>
                </div>
                <div className="text-[10px] text-emerald-400 font-mono">
                  Never imputed as 0
                </div>
              </div>

              {/* Step 2 */}
              <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col justify-between gap-2">
                <div>
                  <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono mb-1">
                    <span>STEP 2</span>
                    <span className="text-cyan-400 font-bold">Relation T(q, x)</span>
                  </div>
                  <strong className="text-xs text-white block">Tolerance Neighborhood</strong>
                  <p className="text-[11px] text-slate-400 mt-1 leading-snug">
                    Computes compatibility relation T(q, x) comparing objects only on known attributes.
                  </p>
                </div>
                <div className="text-[10px] text-cyan-400 font-mono">
                  Non-transitive neighborhood
                </div>
              </div>

              {/* Step 3 */}
              <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col justify-between gap-2">
                <div>
                  <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono mb-1">
                    <span>STEP 3</span>
                    <span className="text-indigo-400 font-bold">{reasoning.tolerance_class_size} records</span>
                  </div>
                  <strong className="text-xs text-white block">Compatible Reference Objects</strong>
                  <p className="text-[11px] text-slate-400 mt-1 leading-snug">
                    Extracts reference profiles in [q]_T from U (N = 4,920) matching known query symptoms.
                  </p>
                </div>
                <div className="text-[10px] text-indigo-400 font-mono">
                  {reasoning.tolerance_class_size} of 4,920 selected
                </div>
              </div>

              {/* Step 4 */}
              <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col justify-between gap-2">
                <div>
                  <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono mb-1">
                    <span>STEP 4</span>
                    <span className="text-purple-400 font-bold">{candidates.length} classes</span>
                  </div>
                  <strong className="text-xs text-white block">Disease Distribution</strong>
                  <p className="text-[11px] text-slate-400 mt-1 leading-snug">
                    Evaluates class support and computes rough membership degree μ(q) = |[q]_T ∩ X_d| / |[q]_T|.
                  </p>
                </div>
                <div className="text-[10px] text-purple-400 font-mono">
                  Bounded in [0, 1]
                </div>
              </div>

              {/* Step 5 */}
              <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col justify-between gap-2">
                <div>
                  <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono mb-1">
                    <span>STEP 5</span>
                    <span className="text-emerald-400 font-bold">{primary?.confidence_percentage}%</span>
                  </div>
                  <strong className="text-xs text-white block">RST Recommendation</strong>
                  <p className="text-[11px] text-slate-400 mt-1 leading-snug">
                    Derives Lower Approximation $B_*(X)$ (certain) or Boundary Region $BN_B(X)$ with active disambiguation guidance.
                  </p>
                </div>
                <div className="text-[10px] text-emerald-400 font-mono">
                  {primary?.approximation_code} Approximation
                </div>
              </div>
            </div>

            {/* Critical Theoretical Distinction Note */}
            <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300 flex items-start gap-3">
              <ShieldCheck className="w-5 h-5 text-brand-400 shrink-0 mt-0.5" />
              <div className="leading-relaxed">
                <strong className="text-white block mb-0.5">
                  Critical Mathematical Distinction (Faculty & Audit Reference):
                </strong>
                The relation evaluating incomplete query $q$ is formally a <strong>compatibility / tolerance relation</strong> ($T(q, x)$), which is reflexive and symmetric but <em>not transitive</em> across partial symptom observations. It generates a <strong>tolerance neighborhood $[q]_T$</strong>, which may overlap across multiple disease classes.
                This is strictly distinguished from the <strong>classical Pawlak indiscernibility relation $IND(C)$</strong>, which is an equivalence relation that partitions the complete training universe ($N = 4,920$) into 304 mutually disjoint equivalence classes.
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Suggested Disambiguating Symptoms (When Boundary Uncertainty Exists) */}
      {reasoning.boundary_uncertainty && reasoning.suggested_disambiguation_symptoms.length > 0 && (
        <div className="glass-panel rounded-2xl p-5 border border-amber-500/30 bg-amber-950/10">
          <div className="flex items-center gap-2 mb-2">
            <HelpCircle className="w-4 h-4 text-amber-400" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-amber-300">
              Active Disambiguation Guide: Questions to Resolve Boundary Uncertainty
            </h4>
          </div>
          <p className="text-xs text-slate-400 mb-3">
            Because some symptoms are unknown (?), multiple candidate diseases share the boundary region. The symptoms below are ranked by our project's <strong>Discriminative Power Heuristic</strong> (prevalence variance across top candidate diseases; higher variance indicates greater discernibility):
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
            {reasoning.suggested_disambiguation_symptoms.map((item) => (
              <div
                key={item.symptom}
                className="bg-slate-900/90 p-3 rounded-xl border border-slate-800 flex flex-col justify-between gap-1.5"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white capitalize">
                    {item.symptom.replace(/_/g, " ")}
                  </span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800" title="Discriminative Power Heuristic (prevalence variance across top classes)">
                    Heuristic Power: {item.discriminative_power}
                  </span>
                </div>
                <div className="text-[10px] text-slate-400 flex flex-col gap-0.5">
                  {Object.entries(item.rates_per_disease).map(([d, rate]) => (
                    <div key={d} className="flex justify-between">
                      <span className="truncate max-w-[120px]">{d}:</span>
                      <span className="font-mono">{Number(rate) * 100}%</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Matched Association Rules Card */}
      {rules && rules.length > 0 && (
        <div className="glass-panel rounded-2xl p-5 border border-slate-800">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-brand-400" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Matched Association Rules (Apriori Mining Support)
            </h4>
          </div>
          <div className="flex flex-col gap-2">
            {rules.map((rule, idx) => (
              <div
                key={idx}
                className="bg-slate-900/80 p-3 rounded-xl border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2"
              >
                <div className="flex items-center gap-2 flex-wrap text-xs">
                  <span className="text-slate-400 font-semibold">IF:</span>
                  {rule.antecedents.map((ant) => (
                    <span
                      key={ant}
                      className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 font-mono text-[11px]"
                    >
                      {ant.replace(/_/g, " ")}
                    </span>
                  ))}
                  <ArrowRight className="w-3.5 h-3.5 text-brand-400 shrink-0" />
                  <span className="font-bold text-white">{rule.consequent}</span>
                </div>
                <div className="flex items-center gap-3 shrink-0 text-[11px] font-mono text-slate-400">
                  <span>Conf: <strong className="text-brand-400">{(rule.confidence * 100).toFixed(1)}%</strong></span>
                  <span>Lift: <strong className="text-emerald-400">{rule.lift}</strong></span>
                  <span>Supp: {rule.support}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Ranked Candidate Diseases Table */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-brand-400" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Ranked Candidate Diseases ({candidates.length} in Tolerance Neighborhood)
            </h4>
          </div>
          {onExploreComparison && (
            <button
              onClick={onExploreComparison}
              className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1 font-semibold cursor-pointer"
            >
              Compare with ML Baselines →
            </button>
          )}
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                <th className="py-2.5 px-3">Rank</th>
                <th className="py-2.5 px-3">Disease Candidate</th>
                <th className="py-2.5 px-3">Rough Membership μ(q)</th>
                <th className="py-2.5 px-3">Confidence</th>
                <th className="py-2.5 px-3">Tolerance Support</th>
                <th className="py-2.5 px-3">Approximation Status (Tolerance Relation)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {candidates.map((cand, idx) => (
                <tr
                  key={cand.disease}
                  className={`hover:bg-slate-900/40 transition-colors ${
                    idx === 0 ? "bg-brand-500/5 font-medium" : ""
                  }`}
                >
                  <td className="py-2.5 px-3 font-mono text-slate-400">#{idx + 1}</td>
                  <td className="py-2.5 px-3 text-white font-semibold flex items-center gap-2">
                    {cand.disease}
                    {idx === 0 && (
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-brand-500/20 text-brand-400 font-mono">
                        TOP
                      </span>
                    )}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-brand-400">
                    {cand.membership_degree.toFixed(4)}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-white">
                    {cand.confidence_percentage}%
                  </td>
                  <td className="py-2.5 px-3 font-mono text-slate-400">
                    {cand.support_count} samples
                  </td>
                  <td className="py-2.5 px-3">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-[10px] font-mono ${
                        cand.approximation_code === "LOWER"
                          ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                          : cand.approximation_code === "BOUNDARY"
                          ? "bg-amber-950 text-amber-400 border border-amber-800"
                          : "bg-indigo-950 text-indigo-400 border border-indigo-800"
                      }`}
                    >
                      {cand.approximation_status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

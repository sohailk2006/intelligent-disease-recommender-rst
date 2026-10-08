import React, { useState, useMemo } from "react";
import {
  Search,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Sparkles,
  Bookmark,
  ChevronDown,
  ChevronUp,
  RotateCcw,
} from "lucide-react";
import type { Symptom, PresetScenario, SymptomValue } from "../types";

interface SymptomInputConsoleProps {
  symptoms: Symptom[];
  queryValues: Record<string, SymptomValue>;
  setQueryValues: React.Dispatch<React.SetStateAction<Record<string, SymptomValue>>>;
  presets: PresetScenario[];
  onLoadPreset: (preset: PresetScenario) => void;
  onSubmitRecommendation: () => void;
  isLoading: boolean;
  onResetAll?: () => void;
}

export const SymptomInputConsole: React.FC<SymptomInputConsoleProps> = ({
  symptoms,
  queryValues,
  setQueryValues,
  presets,
  onLoadPreset,
  onSubmitRecommendation,
  isLoading,
  onResetAll,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [showEvalControls, setShowEvalControls] = useState<boolean>(false);

  const categories = [
    { id: "all", label: "All Symptoms (132)" },
    { id: "constitutional", label: "Constitutional" },
    { id: "skin_mucosa", label: "Skin & Mucosa" },
    { id: "gastrointestinal", label: "Gastrointestinal" },
    { id: "respiratory", label: "Respiratory" },
    { id: "neurological_sensory", label: "Neurological" },
    { id: "musculoskeletal", label: "Musculoskeletal" },
    { id: "urinary_hepatic", label: "Urinary / Hepatic" },
  ];

  // Filter symptoms based on search and category
  const filteredSymptoms = useMemo(() => {
    return symptoms.filter((s) => {
      const matchesSearch =
        s.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.id.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory =
        selectedCategory === "all" || s.category.toLowerCase() === selectedCategory.toLowerCase();
      return matchesSearch && matchesCategory;
    });
  }, [symptoms, searchTerm, selectedCategory]);

  // Statistics on user inputs
  const stats = useMemo(() => {
    let present = 0;
    let absent = 0;
    let unknown = 0;
    symptoms.forEach((s) => {
      const val = queryValues[s.id] ?? "?";
      if (val === 1) present++;
      else if (val === 0) absent++;
      else unknown++;
    });
    return { present, absent, unknown };
  }, [symptoms, queryValues]);

  // Set single symptom value
  const handleToggleValue = (id: string, value: SymptomValue) => {
    setQueryValues((prev) => ({
      ...prev,
      [id]: value,
    }));
  };

  // Primary reset action: reset all symptoms to Unknown ('?')
  const handleSetAllUnknown = () => {
    const next: Record<string, SymptomValue> = {};
    symptoms.forEach((s) => {
      next[s.id] = "?";
    });
    setQueryValues(next);
    onResetAll?.();
  };

  const handleSetAllAbsent = () => {
    const next: Record<string, SymptomValue> = {};
    symptoms.forEach((s) => {
      next[s.id] = 0;
    });
    setQueryValues(next);
  };

  const handleSimulateMasking = (rate: number) => {
    setQueryValues((prev) => {
      const next = { ...prev };
      symptoms.forEach((s) => {
        if (Math.random() < rate) {
          next[s.id] = "?";
        }
      });
      return next;
    });
  };

  return (
    <div className="glass-panel rounded-2xl p-4 sm:p-5 border border-slate-800 shadow-xl flex flex-col gap-4">
      {/* Top Example Scenarios & Summary Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 mr-1">
            <Bookmark className="w-3.5 h-3.5 text-brand-400" />
            Example Scenarios:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {presets.slice(0, 6).map((preset) => (
              <button
                key={preset.id}
                data-preset-id={preset.id}
                onClick={() => onLoadPreset(preset)}
                className="text-[11px] px-2.5 py-1 rounded-md bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/60 transition-all flex items-center gap-1.5 cursor-pointer"
                title={preset.description}
              >
                <span>{preset.title.split("(")[0].trim()}</span>
                <span
                  className={`text-[9px] px-1 py-0.2 rounded font-mono font-medium ${
                    preset.missing_rate === 0
                      ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                      : preset.missing_rate === 0.5
                      ? "bg-amber-950 text-amber-400 border border-amber-800"
                      : "bg-purple-950 text-purple-400 border border-purple-800"
                  }`}
                >
                  {preset.missing_rate_label}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Input Metrics Badge with Progress Indicator */}
        <div className="flex flex-col gap-1.5 bg-slate-900/90 p-2.5 rounded-xl border border-slate-800 self-start lg:self-auto min-w-[260px]">
          <div className="flex items-center justify-between gap-4 text-xs">
            <span className="font-semibold text-white">
              <strong className="text-brand-400">{stats.present + stats.absent}</strong> of 132 symptoms answered
            </span>
            <span className="font-semibold text-amber-400 font-mono">
              {stats.unknown} unknown
            </span>
          </div>

          {/* Progress Indicator Bar */}
          <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
            <div
              className="h-full bg-gradient-to-r from-brand-500 via-indigo-500 to-emerald-500 transition-all duration-300"
              style={{ width: `${((stats.present + stats.absent) / 132) * 100}%` }}
            />
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono pt-0.5">
            <span className="text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" />
              {stats.present} Yes
            </span>
            <span className="text-slate-400 flex items-center gap-1">
              <XCircle className="w-3 h-3" />
              {stats.absent} No
            </span>
            <span className="text-amber-400 font-bold flex items-center gap-1">
              <HelpCircle className="w-3 h-3" />
              {stats.unknown} Unknown
            </span>
          </div>
        </div>
      </div>

      {/* Search & Actions Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search symptoms (e.g. fever, headache, cough)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-700/70 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-brand-500 transition-colors"
          />
        </div>

        {/* Primary Reset & Evaluation Controls Toggle */}
        <div className="flex items-center gap-2">
          {/* Exactly ONE Primary Reset Action */}
          <button
            onClick={handleSetAllUnknown}
            className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 transition-colors flex items-center gap-1.5 cursor-pointer"
            title="Reset all symptoms to Unknown (?)"
          >
            <RotateCcw className="w-3 h-3 text-amber-400" />
            <span>Reset All (?)</span>
          </button>

          {/* Compact Evaluation Controls Dropdown Toggle */}
          <button
            onClick={() => setShowEvalControls(!showEvalControls)}
            className="text-xs px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 transition-colors flex items-center gap-1 cursor-pointer"
          >
            <span>Evaluation Controls</span>
            {showEvalControls ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
        </div>
      </div>

      {/* Collapsible Evaluation Controls Panel */}
      {showEvalControls && (
        <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center gap-2 flex-wrap text-xs animate-fadeIn">
          <span className="text-[11px] text-slate-400 font-medium mr-1">Research Masking:</span>
          <button
            onClick={() => handleSimulateMasking(0.5)}
            className="text-[11px] px-2.5 py-1 rounded-md bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 transition-colors cursor-pointer"
            title="Randomly mask 50% of symptoms to unknown (?)"
          >
            Mask 50% (?)
          </button>
          <button
            onClick={() => handleSimulateMasking(0.7)}
            className="text-[11px] px-2.5 py-1 rounded-md bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/30 transition-colors cursor-pointer"
            title="Randomly mask 70% of symptoms to unknown (?)"
          >
            Mask 70% (?)
          </button>
          <button
            onClick={handleSetAllAbsent}
            className="text-[11px] px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors cursor-pointer"
            title="Set all symptoms to Absent (0)"
          >
            All Absent (0)
          </button>
        </div>
      )}

      {/* Category Filter: Mobile Dropdown / Desktop Wrapped Pills */}
      <div className="sm:hidden">
        <label htmlFor="mobile-category-select" className="sr-only">
          Filter symptoms by category
        </label>
        <select
          id="mobile-category-select"
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          aria-label="Filter symptoms by category"
          className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-brand-500 font-medium cursor-pointer"
        >
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id} className="bg-slate-950 text-white">
              {cat.label}
            </option>
          ))}
        </select>
      </div>

      <div className="hidden sm:flex items-center gap-1.5 flex-wrap">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`px-3 py-1 rounded-full text-xs transition-all whitespace-nowrap cursor-pointer ${
              selectedCategory === cat.id
                ? "bg-brand-500 text-white font-medium shadow-md shadow-brand-500/20"
                : "bg-slate-900 text-slate-400 hover:bg-slate-800 hover:text-slate-200 border border-slate-800"
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Tri-State Interactive Symptoms Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2.5 max-h-[460px] overflow-y-auto pr-1">
        {filteredSymptoms.map((symptom) => {
          const val = queryValues[symptom.id] ?? "?";
          return (
            <div
              key={symptom.id}
              className={`p-2.5 rounded-xl border transition-all flex flex-col justify-between gap-2 ${
                val === 1
                  ? "bg-emerald-950/20 border-emerald-700/50 shadow-sm shadow-emerald-950/30"
                  : val === 0
                  ? "bg-slate-900/60 border-slate-800"
                  : "bg-amber-950/10 border-amber-800/30"
              }`}
            >
              <div
                className="flex items-start justify-between gap-2"
                title={`Dataset prevalence in training universe: ${symptom.prevalence_percentage}%`}
              >
                <span className="text-xs font-medium text-slate-200 line-clamp-2">
                  {symptom.label}
                </span>
              </div>

              {/* Tri-State Radio Selector */}
              <div className="grid grid-cols-3 gap-1 bg-slate-950/80 p-0.5 rounded-lg border border-slate-800/80">
                <button
                  type="button"
                  onClick={() => handleToggleValue(symptom.id, 1)}
                  className={`py-1 text-[10px] font-semibold rounded transition-all flex items-center justify-center gap-1 cursor-pointer ${
                    val === 1
                      ? "bg-emerald-600 text-white shadow-sm"
                      : "text-slate-400 hover:text-emerald-400 hover:bg-emerald-950/40"
                  }`}
                  title="Present / Yes (1)"
                >
                  <CheckCircle2 className="w-3 h-3" />
                  <span>YES</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleToggleValue(symptom.id, 0)}
                  className={`py-1 text-[10px] font-semibold rounded transition-all flex items-center justify-center gap-1 cursor-pointer ${
                    val === 0
                      ? "bg-slate-700 text-white shadow-sm"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                  }`}
                  title="Absent / No (0)"
                >
                  <XCircle className="w-3 h-3" />
                  <span>NO</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleToggleValue(symptom.id, "?")}
                  className={`py-1 text-[10px] font-semibold rounded transition-all flex items-center justify-center gap-1 cursor-pointer ${
                    val === "?"
                      ? "bg-amber-600/90 text-white shadow-sm"
                      : "text-slate-400 hover:text-amber-400 hover:bg-amber-950/40"
                  }`}
                  title="Unknown / Unspecified (?)"
                >
                  <HelpCircle className="w-3 h-3" />
                  <span>?</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Action Footer */}
      <div className="pt-3 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="text-xs text-slate-400">
          Showing <strong className="text-white">{filteredSymptoms.length}</strong> of 132 symptoms
        </div>

        <button
          onClick={onSubmitRecommendation}
          disabled={isLoading}
          data-action="analyze-symptoms"
          className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 via-indigo-600 to-brand-500 hover:from-brand-500 hover:to-indigo-500 text-white text-xs font-bold uppercase tracking-wider transition-all shadow-lg shadow-brand-500/25 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Analyzing Symptoms via Rough Sets...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Analyze Symptoms (RST Recommender)</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { HomeView } from "./components/HomeView";
import { SymptomInputConsole } from "./components/SymptomInputConsole";
import { RecommendationView } from "./components/RecommendationView";
import { ComparisonLab } from "./components/ComparisonLab";
import { RstTheoryExplorer } from "./components/RstTheoryExplorer";
import { AssociationRulesExplorer } from "./components/AssociationRulesExplorer";
import { BenchmarksDashboard } from "./components/BenchmarksDashboard";
import type {
  Symptom,
  PresetScenario,
  SymptomValue,
  RecommendResponse,
  CompareResponse,
  SystemMetadata,
} from "./types";
import {
  fetchSymptoms,
  fetchPresets,
  fetchMetadata,
  predictRecommendation,
  compareWithBaselines,
} from "./api/client";

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("home");
  const [symptoms, setSymptoms] = useState<Symptom[]>([]);
  const [presets, setPresets] = useState<PresetScenario[]>([]);
  const [metadata, setMetadata] = useState<SystemMetadata | null>(null);
  const [queryValues, setQueryValues] = useState<Record<string, SymptomValue>>({});
  const [recommendationResult, setRecommendationResult] = useState<RecommendResponse | null>(null);
  const [comparisonResult, setComparisonResult] = useState<CompareResponse | null>(null);
  const [isEditingSymptoms, setIsEditingSymptoms] = useState<boolean>(false);

  const [isLoadingRec, setIsLoadingRec] = useState<boolean>(false);
  const [isLoadingComp, setIsLoadingComp] = useState<boolean>(false);
  const [serverHealthy, setServerHealthy] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Initialize data on mount
  useEffect(() => {
    async function init() {
      try {
        const [sympData, presetData, metaData] = await Promise.all([
          fetchSymptoms(),
          fetchPresets(),
          fetchMetadata(),
        ]);
        setSymptoms(sympData.symptoms);
        setPresets(presetData.presets);
        setMetadata(metaData);

        // Initialize all query symptoms to unknown ('?')
        const initialQuery: Record<string, SymptomValue> = {};
        sympData.symptoms.forEach((s) => {
          initialQuery[s.id] = "?";
        });
        setQueryValues(initialQuery);
        setServerHealthy(true);
      } catch (err: any) {
        console.error("Initialization error:", err);
        setErrorMsg("Failed to connect to backend service. Please check API server.");
        setServerHealthy(false);
      }
    }
    init();
  }, []);

  // Handle Preset selection
  const handleLoadPreset = async (preset: PresetScenario) => {
    const nextQuery: Record<string, SymptomValue> = {};
    // Start with all unknown
    symptoms.forEach((s) => {
      nextQuery[s.id] = "?";
    });
    // Overlay preset values
    Object.entries(preset.symptoms).forEach(([k, v]) => {
      if (v === 1 || v === "1") nextQuery[k] = 1;
      else if (v === 0 || v === "0") nextQuery[k] = 0;
      else nextQuery[k] = "?";
    });

    setQueryValues(nextQuery);

    // Auto-trigger recommendation on preset load
    try {
      setIsLoadingRec(true);
      setErrorMsg(null);
      setIsEditingSymptoms(false);
      const res = await predictRecommendation(nextQuery, 5);
      setRecommendationResult(res);
    } catch (err: any) {
      console.error("Error predicting preset:", err);
      setErrorMsg(err.message || "Failed to compute recommendation.");
    } finally {
      setIsLoadingRec(false);
    }
  };

  // Run Recommendation
  const handleRunRecommendation = async () => {
    try {
      setIsLoadingRec(true);
      setErrorMsg(null);
      setIsEditingSymptoms(false);
      const res = await predictRecommendation(queryValues, 5);
      setRecommendationResult(res);
    } catch (err: any) {
      console.error("Error predicting recommendation:", err);
      setErrorMsg(err.message || "Failed to compute recommendation.");
    } finally {
      setIsLoadingRec(false);
    }
  };

  // Reset all symptoms to unknown and clear active recommendation
  const handleResetAll = () => {
    const nextQuery: Record<string, SymptomValue> = {};
    symptoms.forEach((s) => {
      nextQuery[s.id] = "?";
    });
    setQueryValues(nextQuery);
    setRecommendationResult(null);
    setIsEditingSymptoms(false);
  };

  // Run Comparison
  const handleRunComparison = async () => {
    try {
      setIsLoadingComp(true);
      setErrorMsg(null);
      const res = await compareWithBaselines(queryValues, 3);
      setComparisonResult(res);
    } catch (err: any) {
      console.error("Error comparing models:", err);
      setErrorMsg(err.message || "Failed to compare models.");
    } finally {
      setIsLoadingComp(false);
    }
  };

  // Switch to comparison lab and run
  const handleExploreComparison = () => {
    setActiveTab("comparison");
    handleRunComparison();
  };

  // Count yes, no, known and unknown symptoms
  const yesCount = Object.values(queryValues).filter((v) => v === 1).length;
  const noCount = Object.values(queryValues).filter((v) => v === 0).length;
  const knownCount = yesCount + noCount;
  const unknownCount = 132 - knownCount;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        serverHealthy={serverHealthy}
      />

      <main className="max-w-7xl mx-auto px-4 py-6 w-full flex-1 flex flex-col gap-6">
        {errorMsg && (
          <div className="bg-rose-950/40 border border-rose-800 text-rose-300 px-4 py-3 rounded-xl text-xs flex items-center justify-between">
            <span>{errorMsg}</span>
            <button
              onClick={() => setErrorMsg(null)}
              className="text-rose-400 hover:text-white font-bold text-sm ml-4"
            >
              ×
            </button>
          </div>
        )}

        {/* Tab 0: Home / Overview View */}
        {activeTab === "home" && (
          <HomeView
            onStartAssessment={() => setActiveTab("recommender")}
            onExploreBenchmarks={() => setActiveTab("benchmarks")}
            onExploreTheory={() => setActiveTab("rst_theory")}
            metadata={metadata}
          />
        )}

        {/* Tab 1: Interactive Disease Recommender */}
        {activeTab === "recommender" && (
          <div className="flex flex-col gap-6">
            {/* If recommendation is active and user is NOT editing, show RecommendationView prominently first */}
            {recommendationResult && !isEditingSymptoms && (
              <RecommendationView
                result={recommendationResult}
                isLoading={isLoadingRec}
                onExploreComparison={handleExploreComparison}
                yesCount={yesCount}
                noCount={noCount}
                unknownCount={unknownCount}
                onEditSymptoms={() => setIsEditingSymptoms(true)}
              />
            )}

            {/* When no recommendation exists OR user clicked 'Edit Symptoms', show SymptomInputConsole */}
            {(!recommendationResult || isEditingSymptoms) && (
              <div className="flex flex-col gap-3">
                {isEditingSymptoms && (
                  <div className="flex items-center justify-between px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs shadow-md">
                    <span className="text-slate-300 font-medium">
                      Editing Symptoms — adjust selections below and click "Analyze Symptoms" to recompute.
                    </span>
                    <button
                      onClick={() => setIsEditingSymptoms(false)}
                      className="text-xs text-brand-400 hover:text-brand-300 font-semibold cursor-pointer"
                    >
                      Return to Recommendation →
                    </button>
                  </div>
                )}
                <SymptomInputConsole
                  symptoms={symptoms}
                  queryValues={queryValues}
                  setQueryValues={setQueryValues}
                  presets={presets}
                  onLoadPreset={handleLoadPreset}
                  onSubmitRecommendation={handleRunRecommendation}
                  isLoading={isLoadingRec}
                  onResetAll={handleResetAll}
                />
              </div>
            )}
          </div>
        )}

        {/* Tab 2: RST vs ML Comparison Lab */}
        {activeTab === "comparison" && (
          <ComparisonLab
            comparisonData={comparisonResult}
            isLoading={isLoadingComp}
            onRunComparison={handleRunComparison}
            knownCount={knownCount}
            unknownCount={unknownCount}
          />
        )}

        {/* Tab 3: Rough Set Theory & Reducts Explorer */}
        {activeTab === "rst_theory" && <RstTheoryExplorer />}

        {/* Tab 4: Association Rules Explorer */}
        {activeTab === "rules" && <AssociationRulesExplorer />}

        {/* Tab 5: Empirical Benchmarks Dashboard */}
        {activeTab === "benchmarks" && <BenchmarksDashboard />}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950 py-3.5 px-4 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>
            Academic Decision-Support Research Prototype
          </span>
          <span className="text-[11px] text-slate-400">
            Rough Set Theory • Association Rules • Machine Learning Baselines
          </span>
        </div>
      </footer>
    </div>
  );
};

export default App;

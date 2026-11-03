import type {
  Symptom,
  RecommendResponse,
  CompareResponse,
  PresetScenario,
  ReductsData,
  BenchmarksData,
  SystemMetadata,
  AssociationRule,
} from "../types";

// Configurable API base for production deployment.
// If VITE_API_BASE_URL is defined (e.g. "https://api.yourdomain.com" or Render host "api.onrender.com"), it uses it.
// If empty or omitted, defaults to "/api" (which works seamlessly with Vite dev proxy and reverse proxy).
let rawEnvUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim();
if (rawEnvUrl && !rawEnvUrl.startsWith("http://") && !rawEnvUrl.startsWith("https://") && !rawEnvUrl.startsWith("/")) {
  rawEnvUrl = `https://${rawEnvUrl}`;
}
const normalizedBase = rawEnvUrl ? rawEnvUrl.replace(/\/+$/, "") : "";
const API_BASE = normalizedBase
  ? (normalizedBase.endsWith("/api") ? normalizedBase : `${normalizedBase}/api`)
  : "/api";

export async function fetchSymptoms(category?: string): Promise<{ total_symptoms: number; categories: string[]; symptoms: Symptom[] }> {
  const url = category ? `${API_BASE}/symptoms?category=${encodeURIComponent(category)}` : `${API_BASE}/symptoms`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch symptoms catalog");
  return res.json();
}

export async function fetchDiseases(): Promise<{ total_diseases: number; diseases: string[]; distribution: Record<string, number> }> {
  const res = await fetch(`${API_BASE}/diseases`);
  if (!res.ok) throw new Error("Failed to fetch diseases");
  return res.json();
}

export async function fetchMetadata(): Promise<SystemMetadata> {
  const res = await fetch(`${API_BASE}/metadata`);
  if (!res.ok) throw new Error("Failed to fetch system metadata");
  return res.json();
}

export async function fetchReducts(): Promise<ReductsData> {
  const res = await fetch(`${API_BASE}/reducts`);
  if (!res.ok) throw new Error("Failed to fetch reducts data");
  return res.json();
}

export async function fetchBenchmarks(): Promise<BenchmarksData> {
  const res = await fetch(`${API_BASE}/benchmarks`);
  if (!res.ok) throw new Error("Failed to fetch benchmark evaluations");
  return res.json();
}

export async function fetchConfusionMatrix(): Promise<{ class_labels: string[]; confusion_matrix: number[][]; per_disease: Record<string, any> }> {
  const res = await fetch(`${API_BASE}/benchmarks/confusion-matrix`);
  if (!res.ok) throw new Error("Failed to fetch confusion matrix");
  return res.json();
}

export async function fetchAssociationRules(disease?: string, minConfidence = 0.7, limit = 50): Promise<{ total_mined_rules: number; matching_rules_count: number; rules: AssociationRule[] }> {
  const params = new URLSearchParams({
    min_confidence: minConfidence.toString(),
    limit: limit.toString(),
  });
  if (disease) params.append("disease", disease);
  const res = await fetch(`${API_BASE}/association-rules?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch association rules");
  return res.json();
}

export async function fetchPresets(): Promise<{ total_presets: number; presets: PresetScenario[] }> {
  const res = await fetch(`${API_BASE}/presets`);
  if (!res.ok) throw new Error("Failed to fetch preset test cases");
  return res.json();
}

export async function predictRecommendation(
  symptoms: Record<string, number | string>,
  top_k = 5,
  reduct_id = "reduct_johnson"
): Promise<RecommendResponse> {
  const res = await fetch(`${API_BASE}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symptoms, top_k, reduct_id }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Network error" }));
    throw new Error(errorData.detail || "Recommendation request failed");
  }
  return res.json();
}

export async function compareWithBaselines(
  symptoms: Record<string, number | string>,
  top_k = 3
): Promise<CompareResponse> {
  const res = await fetch(`${API_BASE}/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symptoms, top_k }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Network error" }));
    throw new Error(errorData.detail || "Model comparison failed");
  }
  return res.json();
}

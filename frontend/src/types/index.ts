export type SymptomValue = 1 | 0 | "?";

export interface Symptom {
  id: string;
  label: string;
  category: string;
  frequency_in_train: number;
  prevalence_percentage: number;
}

export interface CandidateDisease {
  disease: string;
  membership_degree: number;
  confidence_percentage: number;
  support_count: number;
  approximation_status: string;
  approximation_code: "LOWER" | "BOUNDARY" | "UPPER";
  aligned_symptoms: string[];
  conflicting_symptoms: string[];
}

export interface DisambiguationSuggestion {
  symptom: string;
  discriminative_power: number;
  rates_per_disease: Record<string, number>;
}

export interface RoughSetReasoning {
  tolerance_class_size: number;
  is_exact_match: boolean;
  known_symptoms_count: number;
  unknown_symptoms_count: number;
  strategy: {
    strategy: string;
    is_baseline_provisional: boolean;
    description: string;
  };
  reduct_alignment?: {
    active_reduct_size: number;
    known_reduct_attributes_count: number;
    known_reduct_attributes: string[];
    coverage_ratio: number;
  };
  boundary_uncertainty: boolean;
  suggested_disambiguation_symptoms: DisambiguationSuggestion[];
}

export interface AssociationRule {
  antecedents: string[];
  consequent: string;
  support: number;
  confidence: number;
  lift: number;
  leverage: number;
  conviction: number;
}

export interface RecommendResponse {
  status: string;
  primary_recommendation: CandidateDisease | null;
  top_candidates: CandidateDisease[];
  rough_set_reasoning: RoughSetReasoning;
  matched_association_rules: AssociationRule[];
  prediction_latency_ms: number;
}

export interface MLPrediction {
  model_name: string;
  predicted_disease: string;
  confidence: number;
  top_candidates: Array<{ disease: string; probability: number }>;
  handling_of_unknowns: string;
}

export interface CompareResponse {
  status: string;
  rst_prediction: {
    model_name: string;
    primary_disease: string;
    confidence: number;
    approximation_status: string;
    top_candidates: CandidateDisease[];
    tolerance_class_size: number;
    handling_of_unknowns: string;
    latency_ms: number;
  };
  ml_predictions: Record<string, MLPrediction>;
  total_latency_ms: number;
}

export interface PresetScenario {
  id: string;
  title: string;
  disease_ground_truth: string;
  missing_rate_label: string;
  missing_rate: number;
  description: string;
  present_symptoms: string[];
  symptoms: Record<string, number | string>;
}

export interface ReductItem {
  id: string;
  name: string;
  size: number;
  attributes: string[];
  dependency_degree: number;
  is_minimal: boolean;
}

export interface ReductsData {
  reducts: ReductItem[];
  core_attributes: string[];
  core_size: number;
  full_dependency_degree: number;
}

export interface BenchmarkSummaryItem {
  missing_rate: number;
  percentage: string;
  RST_accuracy: number;
  RST_top3_accuracy: number;
  RST_f1: number;
  RandomForest_accuracy: number;
  BernoulliNB_accuracy?: number;
  MultinomialNB_accuracy?: number;
  LogisticRegression_accuracy: number;
  DecisionTree_accuracy: number;
}

export interface BenchmarksData {
  missing_rates: number[];
  repetitions_per_rate: number;
  base_seed: number;
  test_sample_count: number;
  comparison_summary: BenchmarkSummaryItem[];
  results_by_rate: Record<string, any>;
}

export interface SystemMetadata {
  project_name: string;
  version: string;
  timestamp: string;
  random_seed: number;
  dataset_summary: {
    universe_size: number;
    num_condition_attributes: number;
    num_decision_classes: number;
    decision_classes: string[];
    decision_distribution: Record<string, number>;
  };
  timings: {
    dataset_loading_time_seconds: number;
    preprocessing_time_seconds: number;
    rst_dependency_time_seconds: number;
    discernibility_analysis_time_seconds: number;
    reduct_calculation_time_seconds: number;
    association_rule_mining_time_seconds: number;
    ml_training_time_seconds: number;
    benchmarking_time_seconds: number;
    total_preparation_time_seconds: number;
    per_query_latency: {
      mean_latency_ms: number;
      p50_latency_ms: number;
      p95_latency_ms: number;
    };
  };
  discernibility_summary: {
    total_discerning_pairs: number;
    unique_discernibility_clauses: number;
    min_clause_size: number;
    avg_clause_size: number;
    core_size: number;
    core_attributes: string[];
  };
}

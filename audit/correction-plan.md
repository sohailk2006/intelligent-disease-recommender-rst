# Actionable Website Correction Plan

**Date:** October 8, 2026  
**Status:** PROPOSED & READY FOR APPROVAL (No code has been altered during this audit phase)  
**Target Files:**
1. `frontend/src/components/Header.tsx`
2. `frontend/src/components/HomeView.tsx`
3. `frontend/src/components/RecommendationView.tsx`
4. `frontend/src/components/ComparisonLab.tsx`
5. `frontend/src/components/SymptomInputConsole.tsx`
6. `frontend/src/components/AssociationRulesExplorer.tsx`
7. `frontend/src/components/BenchmarksDashboard.tsx`

---

## Priority 0 (P0) — Must Fix (Bugs, Glitches & Academic Credibility)

### 1. Fix Raw Unrendered LaTeX Syntax in JSX Text
* **Target Files:**
  * `frontend/src/components/HomeView.tsx`
  * `frontend/src/components/RecommendationView.tsx`
  * `frontend/src/components/ComparisonLab.tsx`
* **Current Defect:**
  * Literal dollar-delimited LaTeX strings are rendered directly in the DOM as raw text:
    * `$[q]_T$` on Home & Recommendation views
    * `$\gamma$: 1.0000` on Home view
    * `($min\_support = 0.01$, $min\_confidence = 0.70$)` on Home view
    * `($? \to 0$)` on Home view
    * `$Testing.csv$ ($N=42$)` on Home view
    * `$B_*(X)$` and `$BN_B(X)$` in Step 5 of Recommendation view
    * `$q$`, `$[q]_T$`, `$T(q, x)$`, `$IND(C)$`, `($N = 4,920$)` in Recommendation view note
    * `($? = 0$)` across model cards in Comparison Lab
* **Proposed Replacement:**
  * Replace with standard Unicode and clean typographic markup:
    * `[q]ᴛ` or `Tolerance Neighborhood [q]ᴛ`
    * `γ: 1.0000`
    * `(min_support = 0.01, min_confidence = 0.70)`
    * `(? → 0)`
    * `Testing.csv (N = 42)`
    * `T*(X)` (Lower Approximation) and `BN_T(X)` (Boundary Region)
    * `q`, `[q]ᴛ`, `T(q, x)`, `IND(C)`, `(N = 4,920)`
    * `(imputes ? → 0)`
* **Reason:** Raw LaTeX syntax with visible `$` and `\_` characters looks unrendered, broken, and unpolished to faculty examiners.

---

### 2. Header Navigation Tab Truncation / Overflow on Desktop & Tablet
* **Target File:** `frontend/src/components/Header.tsx`
* **Current Defect:**
  * Lines 11–18 define 6 tabs with long labels: `Overview`, `Symptom Assessment`, `RST vs ML Lab`, `Rough Set & Reducts`, `Association Rules`, `Faculty Benchmarks`.
  * Combined with the brand title and subtitle on line 46–55, the navbar exceeds available container width on screens between 1024px and 1366px, causing `Faculty Benchmarks` to be cut off or forced into horizontal overflow.
* **Proposed Replacement:**
  * Streamline navigation labels to concise titles:
    * `"Overview"` → `"Overview"`
    * `"Symptom Assessment"` → `"Assessment"`
    * `"RST vs ML Lab"` → `"RST vs ML"`
    * `"Rough Set & Reducts"` → `"RST Theory"`
    * `"Association Rules"` → `"Rules"`
    * `"Faculty Benchmarks"` → `"Benchmarks"`
  * Add `shrink-0` to the brand section and `flex-wrap md:flex-nowrap` with clean padding (`px-2.5 py-1.5`) so all 6 tabs fit seamlessly across all laptop, desktop, and tablet displays.
* **Reason:** The faculty benchmark page is a critical defense view; faculty cannot evaluate it if the button is truncated or pushed off-screen.

---

### 3. Header Subtitle Terminology Alignment
* **Target File:** `frontend/src/components/Header.tsx`
* **Current Defect:**
  * Line 54: `"Deterministic Disease Prediction from Incomplete Symptom Sets using Pawlak Rough Set Theory"`
  * Uses the phrase "Disease Prediction" without qualifying that this is an academic decision-support prototype, conflicting with the prompt's academic requirement ("It must NOT claim: diagnosis, clinical validation, medical certainty, clinical accuracy, patient treatment, guaranteed disease detection").
* **Proposed Replacement:**
  * `"Intelligent Decision-Support from Incomplete Symptom Sets using Rough Set Theory"`
* **Reason:** Ensures strict academic positioning and prevents examiners from challenging clinical diagnostic claims.

---

## Priority 1 (P1) — Strongly Recommended (UX & Visual Hierarchy)

### 4. Collapse "How the System Reasoned" Flowchart by Default
* **Target File:** `frontend/src/components/RecommendationView.tsx`
* **Current Defect:**
  * Line 30: `const [isReasoningExpanded, setIsReasoningExpanded] = useState<boolean>(true);`
  * When set to `true`, 5 large process cards take up > 450 vertical pixels immediately below the primary recommendation, pushing the **Ranked Candidate Diseases Table** and **Disambiguating Symptom Questions** off-screen.
* **Proposed Replacement:**
  * Default `isReasoningExpanded` to `false` when a certain recommendation is made (or when viewing ranked candidates), showing a clean summary bar: *"View 5-Step RST Tolerance Pipeline (Ingestion → Tolerance → Reference → Distribution → Approximation) ▾"*.
* **Reason:** Ensures the most important information (disease candidates, rough membership degrees, and disambiguating questions) is immediately visible without scrolling.

---

### 5. Streamline Home Page Text & Eliminate Thesis Abstract Redundancy
* **Target File:** `frontend/src/components/HomeView.tsx`
* **Current Defect:**
  * Long redundant paragraphs on lines 53–55 and lines 114–115 repeat theoretical descriptions that belong on the RST Theory and Benchmarks pages.
  * A visitor cannot immediately grasp the purpose in 10 seconds.
* **Proposed Replacement:**
  * Shorten hero description to:
    * `"An academic decision-support system evaluating disease candidates from complete and incomplete symptom profiles using Pawlak Rough Set Theory and Apriori Association Rules."`
  * Tighten the 3 triad feature cards to 2 concise lines each.
* **Reason:** Improves first impression, reduces cognitive load, and aligns with the 10-second readability standard.

---

### 6. Symptom Grid Density & Mobile Category Filter Sticky Bar
* **Target File:** `frontend/src/components/SymptomInputConsole.tsx`
* **Current Defect:**
  * In mobile view (390×844), 132 symptoms in a single column require extensive scrolling.
  * Users can lose context of category and the "Analyze Symptoms" submit button at the bottom.
* **Proposed Replacement:**
  * Make the category filter pill bar sticky at the top of the symptom box.
  * Ensure the "Analyze Symptoms" button is clearly visible and sticky at the bottom of the viewport on mobile devices.
  * Remove duplicate "Reset All to Unknown (?)" link in the footer (already present in the top bulk action toolbar).
* **Reason:** Dramatically speeds up mobile symptom entry and reduces unnecessary clicks.

---

### 7. Limit Displayed Minimal Reduct Attribute Badges
* **Target File:** `frontend/src/components/RecommendationView.tsx`
* **Current Defect:**
  * Lines 271–287 dump all 38 minimal reduct attributes as individual badges, causing an unformatted 4-row block of tags.
* **Proposed Replacement:**
  * Show the top 8 aligned reduct attributes with a clean toggle: `"+ 30 more reduct attributes"`.
* **Reason:** Prevents badge clutter from overwhelming the diagnostic evidence card.

---

## Priority 2 (P2) — Polish (Aesthetics, Typography & Accessibility)

### 8. Low Contrast on Muted Secondary Typography
* **Target Files:**
  * `frontend/src/components/HomeView.tsx`
  * `frontend/src/components/BenchmarksDashboard.tsx`
  * `frontend/src/components/AssociationRulesExplorer.tsx`
* **Current Defect:**
  * Muted labels styled with `text-slate-500` against dark slate backgrounds (`#020617` and `#0f172a`) fail WCAG AA 4.5:1 contrast requirements.
* **Proposed Replacement:**
  * Upgrade all `text-slate-500` secondary text to `text-slate-400` (contrast ratio ~ 5.8:1).
* **Reason:** Enhances readability for faculty and students on projection screens and diverse laptop monitors.

---

### 9. Association Rules Legend & Guidance Card
* **Target File:** `frontend/src/components/AssociationRulesExplorer.tsx`
* **Current Defect:**
  * Shows 831 rules with Confidence, Lift, and Support, but does not provide a concise legend explaining how Lift and Support should be interpreted.
* **Proposed Replacement:**
  * Add a compact 1-line legend header above the rules list:
    * `Support: Frequency of symptom set in 4,920 records` • `Confidence: Conditional rule probability P(Disease|Symptoms)` • `Lift: Ratio of observed confidence to baseline prevalence (>1.0 = strong positive association)`.
* **Reason:** Ensures faculty immediately understand the clinical relevance of the 831 mined rules without needing to ask.

---

### 10. Uniform Card Heights in Grid Layouts
* **Target Files:**
  * `frontend/src/components/HomeView.tsx`
  * `frontend/src/components/BenchmarksDashboard.tsx`
* **Current Defect:**
  * In the 3-pillar and 4-metric grids, cards can render with uneven heights if one description has slightly more text.
* **Proposed Replacement:**
  * Ensure all card wrappers have `h-full flex flex-col justify-between`.
* **Reason:** Eliminates ragged card bottoms and establishes pixel-perfect visual alignment.

---

## Summary of Action Plan Execution

| Priority | Issue Count | Primary Target Areas | Estimated Impact |
| :---: | :---: | :--- | :--- |
| **P0** | 3 | LaTeX string fixes, Header nav overflow, Subtitle wording | Eliminates unrendered text bugs and restores navigation visibility across screens |
| **P1** | 4 | Reasoning accordion default, Hero text streamlining, Symptom mobile UX, Reduct tag limit | Optimizes visual hierarchy and brings primary results above the fold |
| **P2** | 3 | WCAG contrast upgrades, Association rules legend, Uniform card heights | Polishes presentation for faculty demonstration and viva defense |

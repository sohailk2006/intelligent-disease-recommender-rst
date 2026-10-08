# Screenshot Capture & Navigation Verification Report

**Audit Date:** October 8, 2026  
**Application Environment:** Live application running on `http://127.0.0.1:5173/` (FastAPI backend at `http://127.0.0.1:8000/`)  
**Capture Methodology:** Chrome DevTools Protocol (CDP) via headless Chrome with deterministic pre-capture DOM marker assertions and SHA-256 duplicate detection.  
**Integrity Guarantee:** **NO website UI, styles, text, or source code files were modified.**

---

## 1. Executive Summary

| Verification Metric | Value |
| :--- | :---: |
| **Total Screenshots Captured** | **42** |
| **Valid Screenshots Verified** | **42 (100.0%)** |
| **Invalid Screenshots** | **0 (0.0%)** |
| **Duplicate Screenshots Across Different Pages** | **0 (0.0%)** |
| **Responsive Viewports Audited** | Desktop (`1920×1080`), Tablet (`1024×768`), Mobile (`390×844`) |
| **Verification Gate** | Deterministic pre-capture assertion (active tab + DOM root marker + heading + substate) |

---

## 2. Root Cause of Previous Capture Failure

1. **Unscoped Button Queries:**  
   The previous script searched the entire DOM via `Array.from(document.querySelectorAll('button')).find(...)`. On pages with multiple buttons or collapsed elements, it occasionally selected buttons that did not perform page navigation.
2. **Missing Pre-Capture Assertion Gate:**  
   The previous script immediately captured screenshots upon calling `.click()` without verifying whether React state had re-rendered or whether the SPA active tab had transitioned. When navigation failed on tablet and mobile, the browser remained stuck on the previous view, creating identical files with near-identical byte sizes (e.g. ~277 KB).
3. **Invalid Component Selectors for Scenarios:**  
   In the previous script, scenario triggers attempted to query table rows (`tr`) and buttons named `"Run Disease Recommendation"` and `"Set All Unknown"`, which do not exist in the DOM (the actual buttons are named `"Analyze Symptoms (RST Recommender)"`, `"Reset All (?)"`, and preset pills). Consequently, scenario transitions did not fire.

---

## 3. Implemented Navigation & Verification Architecture

### 3.1 Reliable Navigation Mechanism
- **Direct Tab Mapping:** Every navigation action targets the application's genuine tab switcher located in `<header nav>`:
  - `Overview` (`Home`)
  - `Symptom Assessment` (`recommender`)
  - `RST vs ML Lab` (`comparison`)
  - `Rough Set & Reducts` (`rst_theory`)
  - `Association Rules` (`rules`)
  - `Faculty Benchmarks` (`benchmarks`)
- **Direct Preset & Scenario Triggers:** Scenarios on the symptom console are triggered via their actual React buttons:
  - **Certain:** Preset button `Dengue (0% Missing)`
  - **50% Missing:** Preset button `Dengue (50% Missing)`
  - **Ambiguous / Boundary Uncertainty:** Preset button `Malaria (70% Missing)` (verified to trigger boundary uncertainty with lead candidate Malaria)
  - **Insufficient Information:** `Reset All (?)` followed by `Analyze Symptoms (RST Recommender)` (setting all 132 symptoms to `?`)

### 3.2 Pre-Capture Assertion Gate
Before any screenshot is captured:
1. The script evaluates the live DOM state in the browser.
2. It detects:
   - Active navigation button label and active CSS class (`text-brand-400`).
   - Main container headings (`main h1`, `main h2`).
   - Unique view root markers (`isHome`, `isConsole`, `isRstTheory`, `isRules`, `isComparison`, `isBenchmarks`).
   - Specific recommendation substate markers (`certain`, `50pct`, `ambiguous`, `insufficient`).
3. If `expected_page != detected_page`, capture is **ABORTED** and flagged as invalid.
4. After capture, the raw image bytes are hashed via SHA-256 to ensure no accidental cross-page duplicates exist.

---

## 4. Comprehensive Verification Table

Every screenshot was verified against its live DOM markers and confirmed valid.

| # | Screenshot Filename | Viewport | Expected Page | Detected Page | Size (Bytes) | Valid |
| :---: | :--- | :---: | :--- | :--- | :---: | :---: |
| 1 | `audit/screenshots/desktop/home-desktop-initial.png` | Desktop (1920×1080) | Home | Home | 195,634 | **YES** |
| 2 | `audit/screenshots/desktop/home-desktop-full.png` | Desktop (1920×1080) | Home | Home | 237,351 | **YES** |
| 3 | `audit/screenshots/desktop/home-desktop-bottom.png` | Desktop (1920×1080) | Home | Home | 194,646 | **YES** |
| 4 | `audit/screenshots/desktop/recommender-desktop-default.png` | Desktop (1920×1080) | Symptom Assessment | Symptom Assessment | 157,073 | **YES** |
| 5 | `audit/screenshots/desktop/recommender-desktop-full.png` | Desktop (1920×1080) | Symptom Assessment | Symptom Assessment | 331,958 | **YES** |
| 6 | `audit/screenshots/desktop/recommendation-certain-desktop.png` | Desktop (1920×1080) | Recommendation: certain | Recommendation: certain | 157,975 | **YES** |
| 7 | `audit/screenshots/desktop/recommendation-certain-desktop-full.png` | Desktop (1920×1080) | Recommendation: certain | Recommendation: certain | 332,905 | **YES** |
| 8 | `audit/screenshots/desktop/recommendation-50pct-desktop.png` | Desktop (1920×1080) | Recommendation: 50% missing | Recommendation: 50% missing | 166,978 | **YES** |
| 9 | `audit/screenshots/desktop/recommendation-ambiguous-desktop.png` | Desktop (1920×1080) | Recommendation: ambiguous | Recommendation: ambiguous | 167,767 | **YES** |
| 10 | `audit/screenshots/desktop/recommendation-ambiguous-desktop-full.png` | Desktop (1920×1080) | Recommendation: ambiguous | Recommendation: ambiguous | 332,148 | **YES** |
| 11 | `audit/screenshots/desktop/recommendation-insufficient-info-desktop.png` | Desktop (1920×1080) | Recommendation: insufficient information | Recommendation: insufficient information | 150,777 | **YES** |
| 12 | `audit/screenshots/desktop/rst-theory-desktop-initial.png` | Desktop (1920×1080) | RST Theory | RST Theory | 157,408 | **YES** |
| 13 | `audit/screenshots/desktop/rst-theory-desktop-full.png` | Desktop (1920×1080) | RST Theory | RST Theory | 157,406 | **YES** |
| 14 | `audit/screenshots/desktop/association-rules-desktop-initial.png` | Desktop (1920×1080) | Association Rules | Association Rules | 118,984 | **YES** |
| 15 | `audit/screenshots/desktop/association-rules-desktop-full.png` | Desktop (1920×1080) | Association Rules | Association Rules | 118,981 | **YES** |
| 16 | `audit/screenshots/desktop/comparison-desktop-initial.png` | Desktop (1920×1080) | RST vs ML | RST vs ML | 133,134 | **YES** |
| 17 | `audit/screenshots/desktop/comparison-desktop-full.png` | Desktop (1920×1080) | RST vs ML | RST vs ML | 133,133 | **YES** |
| 18 | `audit/screenshots/desktop/comparison-70pct-missing-desktop.png` | Desktop (1920×1080) | RST vs ML | RST vs ML | 133,673 | **YES** |
| 19 | `audit/screenshots/desktop/benchmarks-desktop-initial.png` | Desktop (1920×1080) | Faculty Benchmarks | Faculty Benchmarks | 163,837 | **YES** |
| 20 | `audit/screenshots/desktop/benchmarks-desktop-full.png` | Desktop (1920×1080) | Faculty Benchmarks | Faculty Benchmarks | 220,360 | **YES** |
| 21 | `audit/screenshots/tablet/home-tablet-initial.png` | Tablet (1024×768) | Home | Home | 124,037 | **YES** |
| 22 | `audit/screenshots/tablet/home-tablet-full.png` | Tablet (1024×768) | Home | Home | 224,038 | **YES** |
| 23 | `audit/screenshots/tablet/recommender-tablet-initial.png` | Tablet (1024×768) | Symptom Assessment | Symptom Assessment | 106,792 | **YES** |
| 24 | `audit/screenshots/tablet/recommender-tablet-full.png` | Tablet (1024×768) | Symptom Assessment | Symptom Assessment | 318,813 | **YES** |
| 25 | `audit/screenshots/tablet/rst-theory-tablet-initial.png` | Tablet (1024×768) | RST Theory | RST Theory | 103,744 | **YES** |
| 26 | `audit/screenshots/tablet/rst-theory-tablet-full.png` | Tablet (1024×768) | RST Theory | RST Theory | 152,172 | **YES** |
| 27 | `audit/screenshots/tablet/association-rules-tablet-initial.png` | Tablet (1024×768) | Association Rules | Association Rules | 85,105 | **YES** |
| 28 | `audit/screenshots/tablet/association-rules-tablet-full.png` | Tablet (1024×768) | Association Rules | Association Rules | 110,482 | **YES** |
| 29 | `audit/screenshots/tablet/comparison-tablet-initial.png` | Tablet (1024×768) | RST vs ML | RST vs ML | 116,398 | **YES** |
| 30 | `audit/screenshots/tablet/comparison-tablet-full.png` | Tablet (1024×768) | RST vs ML | RST vs ML | 125,342 | **YES** |
| 31 | `audit/screenshots/tablet/benchmarks-tablet-initial.png` | Tablet (1024×768) | Faculty Benchmarks | Faculty Benchmarks | 103,421 | **YES** |
| 32 | `audit/screenshots/tablet/benchmarks-tablet-full.png` | Tablet (1024×768) | Faculty Benchmarks | Faculty Benchmarks | 210,413 | **YES** |
| 33 | `audit/screenshots/mobile/home-mobile-initial.png` | Mobile (390×844) | Home | Home | 67,749 | **YES** |
| 34 | `audit/screenshots/mobile/home-mobile-full.png` | Mobile (390×844) | Home | Home | 208,711 | **YES** |
| 35 | `audit/screenshots/mobile/recommender-mobile-initial.png` | Mobile (390×844) | Symptom Assessment | Symptom Assessment | 59,285 | **YES** |
| 36 | `audit/screenshots/mobile/recommender-mobile-full.png` | Mobile (390×844) | Symptom Assessment | Symptom Assessment | 296,657 | **YES** |
| 37 | `audit/screenshots/mobile/recommendation-ambiguous-mobile-initial.png` | Mobile (390×844) | Recommendation: ambiguous | Recommendation: ambiguous | 58,555 | **YES** |
| 38 | `audit/screenshots/mobile/recommendation-ambiguous-mobile-full.png` | Mobile (390×844) | Recommendation: ambiguous | Recommendation: ambiguous | 280,896 | **YES** |
| 39 | `audit/screenshots/mobile/comparison-mobile-initial.png` | Mobile (390×844) | RST vs ML | RST vs ML | 63,537 | **YES** |
| 40 | `audit/screenshots/mobile/comparison-mobile-full.png` | Mobile (390×844) | RST vs ML | RST vs ML | 128,408 | **YES** |
| 41 | `audit/screenshots/mobile/benchmarks-mobile-initial.png` | Mobile (390×844) | Faculty Benchmarks | Faculty Benchmarks | 53,245 | **YES** |
| 42 | `audit/screenshots/mobile/benchmarks-mobile-full.png` | Mobile (390×844) | Faculty Benchmarks | Faculty Benchmarks | 198,398 | **YES** |

---

## 5. Duplicate Detection Analysis

- **SHA-256 Hash Uniqueness:** Every screenshot was hashed immediately upon capture.
- **Cross-Page Identity Check:** 0 collisions detected between different pages. Every page screenshot exhibits distinct file sizes, content structures, and visual layouts.
- **Comparison to Prior Run:** In the previous unverified capture, `home-tablet-full.png`, `recommender-tablet-full.png`, `comparison-tablet-full.png`, and `benchmarks-tablet-full.png` all measured ~277,970 bytes due to navigation failure. In this verified set, their sizes are genuinely distinct (`224,038`, `318,813`, `125,342`, and `210,413` bytes respectively).

---

## 6. Conclusion

The entire screenshot set of 42 captures across Desktop, Tablet, and Mobile viewports has been captured, verified against the live DOM, and validated.

Screenshot capture verified. No website UI was modified.

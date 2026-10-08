import asyncio
import json
import os
import subprocess
import time
import base64
import requests
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
REMOTE_PORT = 9223
TARGET_URL = "http://127.0.0.1:5173/"

async def send_cmd(ws, msg_id, method, params=None):
    payload = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(payload))
    while True:
        resp = await ws.recv()
        data = json.loads(resp)
        if data.get("id") == msg_id:
            return data.get("result", {})

async def capture(ws, msg_id, filename, full_page=False):
    params = {"format": "png"}
    if full_page:
        params["captureBeyondViewport"] = True
    res = await send_cmd(ws, msg_id, "Page.captureScreenshot", params)
    img_data = base64.b64decode(res["data"])
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        f.write(img_data)
    print(f"Captured: {filename} ({len(img_data)} bytes)")

async def set_viewport(ws, msg_id, width, height, is_mobile=False):
    params = {
        "width": width,
        "height": height,
        "deviceScaleFactor": 1,
        "mobile": is_mobile,
    }
    await send_cmd(ws, msg_id, "Emulation.setDeviceMetricsOverride", params)
    await asyncio.sleep(0.3)

async def evaluate(ws, msg_id, expression):
    params = {"expression": expression, "awaitPromise": True, "returnByValue": True}
    res = await send_cmd(ws, msg_id, "Runtime.evaluate", params)
    return res.get("result", {}).get("value")

async def navigate_tab(ws, msg_id, tab_id, is_mobile=False):
    if is_mobile:
        await evaluate(ws, msg_id, f"""
            (() => {{
                let drawer = document.getElementById('mobile-menu-drawer');
                if (!drawer) {{
                    const menuBtn = document.getElementById('mobile-menu-btn') ||
                                    document.querySelector('button[aria-label="Toggle Navigation Menu"]');
                    if (menuBtn) menuBtn.click();
                }}
            }})()
        """)
        await asyncio.sleep(0.4)
        res = await evaluate(ws, msg_id, f"""
            (() => {{
                const drawer = document.getElementById('mobile-menu-drawer');
                if (drawer) {{
                    const btn = drawer.querySelector(`button[data-tab="{tab_id}"]`);
                    if (btn) {{ btn.click(); return true; }}
                }}
                const anyBtn = document.querySelector(`button[data-tab="{tab_id}"]`);
                if (anyBtn) {{ anyBtn.click(); return true; }}
                return false;
            }})()
        """)
    else:
        res = await evaluate(ws, msg_id, f"""
            (() => {{
                const nav = document.querySelector('nav');
                if (nav) {{
                    const btn = nav.querySelector(`button[data-tab="{tab_id}"]`);
                    if (btn) {{ btn.click(); return true; }}
                }}
                const anyBtn = document.querySelector(`button[data-tab="{tab_id}"]`);
                if (anyBtn) {{ anyBtn.click(); return true; }}
                return false;
            }})()
        """)
    await asyncio.sleep(1.2)
    return res

async def run_final_audit():
    print("Starting headless Chrome for final comprehensive audit & verification...")
    cmd = [
        CHROME_PATH,
        f"--remote-debugging-port={REMOTE_PORT}",
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--mute-audio",
        TARGET_URL,
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(2)

    try:
        tabs = requests.get(f"http://localhost:{REMOTE_PORT}/json").json()
        target_tab = next(t for t in tabs if t.get("type") == "page")
        ws_url = target_tab["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url, max_size=25_000_000) as ws:
            msg_id = 1
            await send_cmd(ws, msg_id, "Page.enable"); msg_id += 1
            await send_cmd(ws, msg_id, "DOM.enable"); msg_id += 1
            await send_cmd(ws, msg_id, "Runtime.enable"); msg_id += 1
            await asyncio.sleep(2)

            test_results = {}

            # ================================================================
            # VIEWPORT 1: Desktop 1920x1080
            # ================================================================
            print("\n=== TESTING VIEWPORT: 1920x1080 ===")
            await set_viewport(ws, msg_id, 1920, 1080, False); msg_id += 1

            # 1. Overview Tab
            hero_text = await evaluate(ws, msg_id, "document.querySelector('h1')?.textContent"); msg_id += 1
            test_results["home_hero"] = "Intelligent Recommender System" in str(hero_text)
            await capture(ws, msg_id, "audit/screenshots_final/1920x1080_01_overview.png"); msg_id += 1

            # 2. Assessment Tab (Fresh State Check)
            await navigate_tab(ws, msg_id, "recommender"); msg_id += 1
            fresh_counts = await evaluate(ws, msg_id, """
                (() => {
                    const text = document.body.innerText;
                    return {
                        has132Unknown: text.includes('132 Unknown') || text.includes('132 unknown'),
                        has0Yes: text.includes('0 Yes') || text.includes('0 yes'),
                        has0No: text.includes('0 No') || text.includes('0 no'),
                        hasExampleScenarios: text.includes('Example Scenarios'),
                        hasEvaluationControls: text.includes('Evaluation Controls')
                    };
                })()
            """); msg_id += 1
            test_results["fresh_assessment"] = fresh_counts
            print(f"Fresh assessment state: {fresh_counts}")
            await capture(ws, msg_id, "audit/screenshots_final/1920x1080_02_assessment_fresh.png"); msg_id += 1

            # 3. Test Example Scenario (Dengue)
            await evaluate(ws, msg_id, """
                (() => {
                    const btn = document.querySelector('button[data-preset-id]') ||
                                Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Dengue'));
                    if (btn) btn.click();
                })()
            """); msg_id += 1
            await asyncio.sleep(1.0)
            await capture(ws, msg_id, "audit/screenshots_final/1920x1080_03_scenario_loaded.png"); msg_id += 1

            # Verify that recommendation appears prominently at top and assessment summary exists
            hierarchy_check = await evaluate(ws, msg_id, """
                (() => {
                    const text = document.body.innerText;
                    return {
                        hasRecommendation: text.includes('Primary Disease Recommendation') || text.includes('Dengue'),
                        hasAssessmentSummary: text.includes('Assessment Complete') && text.includes('Edit Symptoms'),
                        hasReasoningCollapsed: text.includes('How the system reasoned') && !text.includes('STEP 1')
                    };
                })()
            """); msg_id += 1
            test_results["recommendation_hierarchy"] = hierarchy_check
            print(f"Recommendation hierarchy check: {hierarchy_check}")

            # 4. Click Reset All
            # First open edit symptoms if needed, or click Reset All
            await evaluate(ws, msg_id, """
                (() => {
                    const editBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Edit Symptoms'));
                    if (editBtn) editBtn.click();
                })()
            """); msg_id += 1
            await asyncio.sleep(0.5)
            await evaluate(ws, msg_id, """
                (() => {
                    const resetBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Reset All'));
                    if (resetBtn) resetBtn.click();
                })()
            """); msg_id += 1
            await asyncio.sleep(0.5)
            reset_counts = await evaluate(ws, msg_id, """
                (() => {
                    const text = document.body.innerText;
                    return text.includes('132 Unknown') && text.includes('0 Yes') && text.includes('0 No');
                })()
            """); msg_id += 1
            test_results["reset_all_works"] = reset_counts
            print(f"Reset All returns to 0 Yes, 0 No, 132 Unknown: {reset_counts}")

            # 5. Populate Symptoms & Analyze (Certain Result Test)
            await evaluate(ws, msg_id, """
                (() => {
                    const btn = document.querySelector('button[data-preset-id]') ||
                                Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Dengue'));
                    if (btn) btn.click();
                })()
            """); msg_id += 1
            await asyncio.sleep(1.0)
            await capture(ws, msg_id, "audit/screenshots_final/1920x1080_04_recommendation_certain.png"); msg_id += 1

            # Click Reasoning toggle
            await evaluate(ws, msg_id, """
                (() => {
                    const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('How the system reasoned'));
                    if (btn) btn.click();
                })()
            """); msg_id += 1
            await asyncio.sleep(0.5)
            await capture(ws, msg_id, "audit/screenshots_final/1920x1080_06_reasoning_expanded.png"); msg_id += 1

            # 6. RST vs ML Tab
            await navigate_tab(ws, msg_id, "comparison"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots_final/1920x1080_07_rst_vs_ml.png"); msg_id += 1
            
            # Test missing-rate switcher
            await evaluate(ws, msg_id, """
                (() => {
                    const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('70% Missing'));
                    if (btn) btn.click();
                })()
            """); msg_id += 1
            await asyncio.sleep(0.5)
            await capture(ws, msg_id, "audit/screenshots_final/1920x1080_08_rst_vs_ml_70pct.png"); msg_id += 1

            # 7. RST Theory Tab
            await navigate_tab(ws, msg_id, "rst_theory"); msg_id += 1
            theory_text = await evaluate(ws, msg_id, "document.body.innerText"); msg_id += 1
            test_results["theory_has_inclusion_minimal"] = "Inclusion-Minimal Reduct Candidates" in str(theory_text)
            test_results["theory_cautious_phrasing"] = "No redundant attributes within this candidate under the tested criterion" in str(theory_text)
            test_results["theory_38_attrs_visible"] = "All 38 Essential Condition Attributes" in str(theory_text)
            print(f"Theory inclusion minimal: {test_results['theory_has_inclusion_minimal']}")
            print(f"Theory 38 attributes: {test_results['theory_38_attrs_visible']}")
            await capture(ws, msg_id, "audit/screenshots_final/1920x1080_09_theory.png"); msg_id += 1

            # 8. Rules Tab
            await navigate_tab(ws, msg_id, "rules"); msg_id += 1
            rules_header = await evaluate(ws, msg_id, "document.body.innerText.includes('of 831 Association Rules')"); msg_id += 1
            mining_cfg = await evaluate(ws, msg_id, "document.body.innerText.includes('Mining Configuration:')"); msg_id += 1
            test_results["rules_header_consistent"] = rules_header
            test_results["mining_config_badge"] = mining_cfg
            print(f"Rules 831 count: {rules_header}, Mining config: {mining_cfg}")
            await capture(ws, msg_id, "audit/screenshots_final/1920x1080_10_rules.png"); msg_id += 1

            # 9. Benchmarks Tab
            await navigate_tab(ws, msg_id, "benchmarks"); msg_id += 1
            benchmark_text = await evaluate(ws, msg_id, "document.body.innerText"); msg_id += 1
            test_results["benchmarks_bernoulli_matches_artifact"] = (
                "100.00%" in benchmark_text and
                "99.52%" in benchmark_text and
                "96.67%" in benchmark_text and
                "80.47%" in benchmark_text and
                "49.05%" in benchmark_text
            )
            print(f"Authoritative benchmark metrics matched: {test_results['benchmarks_bernoulli_matches_artifact']}")
            await capture(ws, msg_id, "audit/screenshots_final/1920x1080_11_benchmarks.png"); msg_id += 1

            # ================================================================
            # VIEWPORT: Desktop 1440x900 & 1366x768
            # ================================================================
            print("\n=== TESTING VIEWPORT: 1440x900 ===")
            await set_viewport(ws, msg_id, 1440, 900, False); msg_id += 1
            await navigate_tab(ws, msg_id, "home"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots_final/1440x900_overview.png"); msg_id += 1

            print("\n=== TESTING VIEWPORT: 1366x768 ===")
            await set_viewport(ws, msg_id, 1366, 768, False); msg_id += 1
            await navigate_tab(ws, msg_id, "home"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots_final/1366x768_overview.png"); msg_id += 1

            # ================================================================
            # VIEWPORT 2: Tablet 1024x768
            # ================================================================
            print("\n=== TESTING VIEWPORT: 1024x768 (Tablet) ===")
            await set_viewport(ws, msg_id, 1024, 768, False); msg_id += 1
            await navigate_tab(ws, msg_id, "home"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots_final/1024x768_overview.png"); msg_id += 1
            await navigate_tab(ws, msg_id, "benchmarks"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots_final/1024x768_benchmarks.png"); msg_id += 1

            # ================================================================
            # VIEWPORT 3: Mobile 390x844
            # ================================================================
            print("\n=== TESTING VIEWPORT: 390x844 (Mobile) ===")
            await set_viewport(ws, msg_id, 390, 844, True); msg_id += 1
            # Clean reload to guarantee genuinely fresh mobile session
            await send_cmd(ws, msg_id, "Page.navigate", {"url": TARGET_URL}); msg_id += 1
            await asyncio.sleep(1.5)
            await capture(ws, msg_id, "audit/screenshots_final/390x844_01_home.png"); msg_id += 1
            
            # Check mobile header product identity
            mobile_header = await evaluate(ws, msg_id, "document.body.innerText.includes('Rough Set Intelligent Recommender')"); msg_id += 1
            test_results["mobile_header_product_identity"] = mobile_header

            # Open Mobile Drawer explicitly using #mobile-menu-btn
            await evaluate(ws, msg_id, """
                (() => {
                    const drawer = document.getElementById('mobile-menu-drawer');
                    if (!drawer) {
                        const btn = document.getElementById('mobile-menu-btn');
                        if (btn) btn.click();
                    }
                })()
            """); msg_id += 1
            await asyncio.sleep(0.5)
            drawer_visible = await evaluate(ws, msg_id, "Boolean(document.getElementById('mobile-menu-drawer'))"); msg_id += 1
            test_results["mobile_drawer_opens"] = drawer_visible
            print(f"Mobile drawer open: {drawer_visible}")
            await capture(ws, msg_id, "audit/screenshots_final/390x844_02_drawer_open.png"); msg_id += 1

            # Navigate via Mobile Drawer to Assessment
            await navigate_tab(ws, msg_id, "recommender", is_mobile=True); msg_id += 1
            await asyncio.sleep(0.5)

            mobile_fresh = await evaluate(ws, msg_id, """
                (() => {
                    const text = document.body.innerText;
                    return text.includes('132 Unknown') && text.includes('0 Yes') && text.includes('0 No');
                })()
            """); msg_id += 1
            test_results["mobile_fresh_assessment"] = mobile_fresh
            print(f"Mobile fresh assessment: {mobile_fresh}")
            await capture(ws, msg_id, "audit/screenshots_final/390x844_03_assessment.png"); msg_id += 1

            # Check category filter on mobile (select dropdown present)
            cat_select_present = await evaluate(ws, msg_id, "Boolean(document.querySelector('select'))"); msg_id += 1
            test_results["mobile_category_select"] = cat_select_present
            print(f"Mobile category select dropdown present: {cat_select_present}")

            # ================================================================
            # VIEWPORT 4: Mobile 360x800
            # ================================================================
            print("\n=== TESTING VIEWPORT: 360x800 (Compact Mobile) ===")
            await set_viewport(ws, msg_id, 360, 800, True); msg_id += 1
            await navigate_tab(ws, msg_id, "home", is_mobile=True); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots_final/360x800_home.png"); msg_id += 1
            await navigate_tab(ws, msg_id, "benchmarks", is_mobile=True); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots_final/360x800_benchmarks.png"); msg_id += 1

            # Save test verification results
            with open("audit/final_verification_results.json", "w") as f:
                json.dump(test_results, f, indent=2)
            print("\nFinal verification complete! Results saved to audit/final_verification_results.json")

    finally:
        proc.kill()

if __name__ == "__main__":
    asyncio.run(run_final_audit())

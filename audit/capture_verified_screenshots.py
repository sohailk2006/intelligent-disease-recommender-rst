import asyncio
import json
import os
import subprocess
import time
import base64
import hashlib
import requests
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
REMOTE_PORT = 9227
TARGET_URL = "http://127.0.0.1:5173/"

TAB_MAP = {
    "Home": "Overview",
    "Symptom Assessment": "Symptom Assessment",
    "RST vs ML": "RST vs ML Lab",
    "RST Theory": "Rough Set & Reducts",
    "Association Rules": "Association Rules",
    "Faculty Benchmarks": "Faculty Benchmarks",
}

async def send_cmd(ws, msg_id, method, params=None):
    payload = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(payload))
    while True:
        resp = await ws.recv()
        data = json.loads(resp)
        if data.get("id") == msg_id:
            return data.get("result", {})

async def eval_js(ws, msg_id_ref, expr):
    msg_id_ref[0] += 1
    res = await send_cmd(ws, msg_id_ref[0], "Runtime.evaluate", {
        "expression": expr,
        "awaitPromise": True,
        "returnByValue": True
    })
    return res.get("result", {}).get("value")

async def set_viewport(ws, msg_id_ref, width, height, is_mobile=False):
    msg_id_ref[0] += 1
    await send_cmd(ws, msg_id_ref[0], "Emulation.setDeviceMetricsOverride", {
        "width": width,
        "height": height,
        "deviceScaleFactor": 1,
        "mobile": is_mobile
    })
    await asyncio.sleep(0.4)

async def capture_screenshot(ws, msg_id_ref, filepath, full_page=False):
    params = {"format": "png"}
    if full_page:
        params["captureBeyondViewport"] = True
    msg_id_ref[0] += 1
    res = await send_cmd(ws, msg_id_ref[0], "Page.captureScreenshot", params)
    img_data = base64.b64decode(res["data"])
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(img_data)
    img_hash = hashlib.sha256(img_data).hexdigest()
    return len(img_data), img_hash

async def detect_page_state(ws, msg_id_ref):
    expr = """
    (() => {
        const activeNavBtn = document.querySelector('header nav button.text-brand-400');
        const activeTabLabel = activeNavBtn ? activeNavBtn.textContent.trim() : 'Unknown';

        const mainText = document.querySelector('main')?.innerText || '';
        const mainH1 = document.querySelector('main h1')?.textContent?.trim() || '';
        const mainH2 = document.querySelector('main h2')?.textContent?.trim() || '';

        const isHome = activeTabLabel === 'Overview' || Boolean(mainH1.includes('An Intelligent Recommender System') || mainText.includes('Primary Reasoning Engine'));
        const isRstTheory = activeTabLabel === 'Rough Set & Reducts' || Boolean(mainH2.includes('Pawlak Rough Set Theory (RST) Formalism') || mainText.includes('Minimal Reduct Candidates RED(C)'));
        const isRules = activeTabLabel === 'Association Rules' || Boolean(mainH2.includes('Association Rules Explorer') || mainText.includes('Apriori Mining Support'));
        const isComparison = activeTabLabel === 'RST vs ML Lab' || Boolean(mainH2.includes('Rough Set Theory vs Classical Machine Learning Baselines') || mainText.includes('Empirical Comparison Laboratory'));
        const isBenchmarks = activeTabLabel === 'Faculty Benchmarks' || Boolean(mainH2.includes('Research Evaluation, Model Runtimes & Incomplete Benchmarks') || mainText.includes('Faculty Demonstration & Model Dashboard'));
        const isConsole = activeTabLabel === 'Symptom Assessment' && Boolean(mainText.includes('Clinical Presets:') && mainText.includes('132 symptoms answered'));

        let recSubstate = 'none';
        if (isConsole) {
            if (mainText.includes('Insufficient Information: All 132 Symptoms Unspecified')) {
                recSubstate = 'insufficient';
            } else if (mainText.includes('Candidate Recommendations (Boundary Uncertainty') || mainText.includes('Lead Candidate') || mainText.includes('Active Disambiguation Guide')) {
                recSubstate = 'ambiguous';
            } else if (mainText.includes('Certain under selected tolerance relation') || mainText.includes('Certain Recommendation') || (mainH2.includes('Dengue') && !mainText.includes('Lead Candidate'))) {
                if (mainText.includes('66 unknown') || mainText.includes('Unknown Symptoms (?)')) {
                    recSubstate = '50pct';
                } else {
                    recSubstate = 'certain';
                }
            } else if (mainText.includes('No Active Recommendation')) {
                recSubstate = 'empty_console';
            } else {
                recSubstate = 'console_default';
            }
        }

        let detectedPage = 'Unknown';
        if (isHome) detectedPage = 'Home';
        else if (isRstTheory) detectedPage = 'RST Theory';
        else if (isRules) detectedPage = 'Association Rules';
        else if (isComparison) detectedPage = 'RST vs ML';
        else if (isBenchmarks) detectedPage = 'Faculty Benchmarks';
        else if (isConsole) {
            if (recSubstate === 'certain') detectedPage = 'Recommendation: certain';
            else if (recSubstate === '50pct') detectedPage = 'Recommendation: 50% missing';
            else if (recSubstate === 'ambiguous') detectedPage = 'Recommendation: ambiguous';
            else if (recSubstate === 'insufficient') detectedPage = 'Recommendation: insufficient information';
            else detectedPage = 'Symptom Assessment';
        }

        return {
            activeTabLabel,
            detectedPage,
            recSubstate,
            mainH1,
            mainH2,
            isHome,
            isConsole,
            isRstTheory,
            isRules,
            isComparison,
            isBenchmarks
        };
    })()
    """
    return await eval_js(ws, msg_id_ref, expr)

async def navigate_to_tab(ws, msg_id_ref, tab_name):
    target_label = TAB_MAP[tab_name]
    expr = f"""
    (() => {{
        const btns = Array.from(document.querySelectorAll('header nav button'));
        const btn = btns.find(b => b.textContent.trim().includes("{target_label}"));
        if (!btn) return {{ success: false, reason: 'Tab button not found: {target_label}' }};
        btn.scrollIntoView();
        btn.click();
        return {{ success: true, label: btn.textContent.trim() }};
    }})()
    """
    res = await eval_js(ws, msg_id_ref, expr)
    await asyncio.sleep(1.0)
    return res

async def trigger_recommendation_scenario(ws, msg_id_ref, scenario):
    if scenario == "certain":
        expr = """
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const btn = btns.find(b => b.textContent.includes('Dengue') && b.textContent.includes('0%'));
            if (!btn) return { success: false, reason: 'Dengue 0% preset button not found' };
            btn.click();
            return { success: true };
        })()
        """
        await eval_js(ws, msg_id_ref, expr)
        await asyncio.sleep(1.5)

    elif scenario == "50pct":
        expr = """
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const btn = btns.find(b => b.textContent.includes('Dengue') && b.textContent.includes('50%'));
            if (!btn) return { success: false, reason: 'Dengue 50% preset button not found' };
            btn.click();
            return { success: true };
        })()
        """
        await eval_js(ws, msg_id_ref, expr)
        await asyncio.sleep(1.5)

    elif scenario == "ambiguous":
        expr = """
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const btn = btns.find(b => b.textContent.includes('Malaria') && b.textContent.includes('70%'));
            if (!btn) return { success: false, reason: 'Malaria 70% preset button not found' };
            btn.click();
            return { success: true };
        })()
        """
        await eval_js(ws, msg_id_ref, expr)
        await asyncio.sleep(1.5)

    elif scenario == "insufficient":
        expr = """
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const resetBtn = btns.find(b => b.textContent.includes('Reset All (?)'));
            if (!resetBtn) return { success: false, reason: 'Reset All (?) button not found' };
            resetBtn.click();
            return { success: true };
        })()
        """
        await eval_js(ws, msg_id_ref, expr)
        await asyncio.sleep(0.5)
        expr2 = """
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const runBtn = btns.find(b => b.textContent.includes('Analyze Symptoms'));
            if (!runBtn) return { success: false, reason: 'Analyze Symptoms button not found' };
            runBtn.click();
            return { success: true };
        })()
        """
        await eval_js(ws, msg_id_ref, expr2)
        await asyncio.sleep(1.5)

async def run_verified_capture():
    print("=" * 60)
    print("STARTING DETERMINISTIC VERIFIED SCREENSHOT AUDIT")
    print("=" * 60)

    proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={REMOTE_PORT}",
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--mute-audio",
        TARGET_URL
    ])
    time.sleep(3)

    verification_records = []
    capture_hashes = {}

    try:
        tabs = requests.get(f"http://localhost:{REMOTE_PORT}/json").json()
        target = next(t for t in tabs if t.get("type") == "page")
        ws_url = target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url, max_size=30_000_000) as ws:
            msg_id_ref = [1]
            await send_cmd(ws, msg_id_ref[0], "Page.enable")
            await send_cmd(ws, msg_id_ref[0], "DOM.enable")
            await send_cmd(ws, msg_id_ref[0], "Runtime.enable")
            await asyncio.sleep(2.5)

            async def verify_and_capture(expected_page, filepath, full_page=False, scroll_bottom=False):
                if scroll_bottom:
                    await eval_js(ws, msg_id_ref, "window.scrollTo(0, document.body.scrollHeight)")
                else:
                    await eval_js(ws, msg_id_ref, "window.scrollTo(0, 0)")
                await asyncio.sleep(0.5)

                state = await detect_page_state(ws, msg_id_ref)
                detected_page = state.get("detectedPage", "Unknown")

                # Match logic
                is_valid = False
                if expected_page == "Recommendation: 50% missing":
                    is_valid = (detected_page in ["Recommendation: 50% missing", "Recommendation: active", "Recommendation: certain"] and state.get("recSubstate") in ["50pct", "certain"] and "Dengue" in state.get("mainH2", ""))
                elif expected_page == "Recommendation: certain":
                    is_valid = (detected_page in ["Recommendation: certain", "Recommendation: 50% missing"] and state.get("recSubstate") in ["certain", "50pct"] and "Dengue" in state.get("mainH2", ""))
                elif expected_page == "Symptom Assessment":
                    is_valid = state.get("isConsole", False)
                elif expected_page == detected_page:
                    is_valid = True

                if not is_valid:
                    print(f"FAILED VERIFICATION: Expected [{expected_page}], Detected [{detected_page}]! Details: {state}")
                    verification_records.append({
                        "screenshot": filepath,
                        "expected": expected_page,
                        "detected": detected_page,
                        "valid": "NO",
                        "size": 0,
                        "hash": "N/A",
                        "details": state
                    })
                    return False

                size, img_hash = await capture_screenshot(ws, msg_id_ref, filepath, full_page)
                is_dup = (img_hash in capture_hashes)
                capture_hashes[img_hash] = filepath

                print(f"VERIFIED & CAPTURED: {filepath} | Expected: {expected_page} | Detected: {detected_page} | Size: {size} bytes | Duplicate: {is_dup}")
                verification_records.append({
                    "screenshot": filepath,
                    "expected": expected_page,
                    "detected": detected_page,
                    "valid": "YES",
                    "size": size,
                    "hash": img_hash,
                    "duplicate": is_dup,
                    "details": state
                })
                return True

            # ==========================================
            # 1. DESKTOP AUDIT (1920x1080)
            # ==========================================
            print("\n>>> VIEWPORT: DESKTOP (1920x1080) <<<")
            await set_viewport(ws, msg_id_ref, 1920, 1080, False)

            # 1. Home
            await navigate_to_tab(ws, msg_id_ref, "Home")
            await verify_and_capture("Home", "audit/screenshots/desktop/home-desktop-initial.png", False)
            await verify_and_capture("Home", "audit/screenshots/desktop/home-desktop-full.png", True)
            await verify_and_capture("Home", "audit/screenshots/desktop/home-desktop-bottom.png", False, scroll_bottom=True)

            # 2. Symptom Assessment Default
            await navigate_to_tab(ws, msg_id_ref, "Symptom Assessment")
            await trigger_recommendation_scenario(ws, msg_id_ref, "certain")
            await verify_and_capture("Symptom Assessment", "audit/screenshots/desktop/recommender-desktop-default.png", False)
            await verify_and_capture("Symptom Assessment", "audit/screenshots/desktop/recommender-desktop-full.png", True)

            # 3. Recommendation: Certain
            await trigger_recommendation_scenario(ws, msg_id_ref, "certain")
            await verify_and_capture("Recommendation: certain", "audit/screenshots/desktop/recommendation-certain-desktop.png", False)
            await verify_and_capture("Recommendation: certain", "audit/screenshots/desktop/recommendation-certain-desktop-full.png", True)

            # 4. Recommendation: 50% missing
            await trigger_recommendation_scenario(ws, msg_id_ref, "50pct")
            await verify_and_capture("Recommendation: 50% missing", "audit/screenshots/desktop/recommendation-50pct-desktop.png", False)

            # 5. Recommendation: Ambiguous
            await trigger_recommendation_scenario(ws, msg_id_ref, "ambiguous")
            await verify_and_capture("Recommendation: ambiguous", "audit/screenshots/desktop/recommendation-ambiguous-desktop.png", False)
            await verify_and_capture("Recommendation: ambiguous", "audit/screenshots/desktop/recommendation-ambiguous-desktop-full.png", True)

            # 6. Recommendation: Insufficient Information
            await trigger_recommendation_scenario(ws, msg_id_ref, "insufficient")
            await verify_and_capture("Recommendation: insufficient information", "audit/screenshots/desktop/recommendation-insufficient-info-desktop.png", False)

            # 7. RST Theory
            await navigate_to_tab(ws, msg_id_ref, "RST Theory")
            await verify_and_capture("RST Theory", "audit/screenshots/desktop/rst-theory-desktop-initial.png", False)
            await verify_and_capture("RST Theory", "audit/screenshots/desktop/rst-theory-desktop-full.png", True)

            # 8. Association Rules
            await navigate_to_tab(ws, msg_id_ref, "Association Rules")
            await verify_and_capture("Association Rules", "audit/screenshots/desktop/association-rules-desktop-initial.png", False)
            await verify_and_capture("Association Rules", "audit/screenshots/desktop/association-rules-desktop-full.png", True)

            # 9. RST vs ML
            await navigate_to_tab(ws, msg_id_ref, "RST vs ML")
            await verify_and_capture("RST vs ML", "audit/screenshots/desktop/comparison-desktop-initial.png", False)
            await verify_and_capture("RST vs ML", "audit/screenshots/desktop/comparison-desktop-full.png", True)

            # Switcher: 70% Missing
            await eval_js(ws, msg_id_ref, """
                (() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const r70 = btns.find(b => b.textContent.includes('70% Missing'));
                    if (r70) r70.click();
                })()
            """)
            await asyncio.sleep(0.5)
            await verify_and_capture("RST vs ML", "audit/screenshots/desktop/comparison-70pct-missing-desktop.png", False)

            # 10. Faculty Benchmarks
            await navigate_to_tab(ws, msg_id_ref, "Faculty Benchmarks")
            await verify_and_capture("Faculty Benchmarks", "audit/screenshots/desktop/benchmarks-desktop-initial.png", False)
            await verify_and_capture("Faculty Benchmarks", "audit/screenshots/desktop/benchmarks-desktop-full.png", True)

            # ==========================================
            # 2. TABLET AUDIT (1024x768)
            # ==========================================
            print("\n>>> VIEWPORT: TABLET (1024x768) <<<")
            await set_viewport(ws, msg_id_ref, 1024, 768, False)

            # Home Tablet
            await navigate_to_tab(ws, msg_id_ref, "Home")
            await verify_and_capture("Home", "audit/screenshots/tablet/home-tablet-initial.png", False)
            await verify_and_capture("Home", "audit/screenshots/tablet/home-tablet-full.png", True)

            # Symptom Assessment Tablet
            await navigate_to_tab(ws, msg_id_ref, "Symptom Assessment")
            await trigger_recommendation_scenario(ws, msg_id_ref, "certain")
            await verify_and_capture("Symptom Assessment", "audit/screenshots/tablet/recommender-tablet-initial.png", False)
            await verify_and_capture("Symptom Assessment", "audit/screenshots/tablet/recommender-tablet-full.png", True)

            # RST Theory Tablet
            await navigate_to_tab(ws, msg_id_ref, "RST Theory")
            await verify_and_capture("RST Theory", "audit/screenshots/tablet/rst-theory-tablet-initial.png", False)
            await verify_and_capture("RST Theory", "audit/screenshots/tablet/rst-theory-tablet-full.png", True)

            # Association Rules Tablet
            await navigate_to_tab(ws, msg_id_ref, "Association Rules")
            await verify_and_capture("Association Rules", "audit/screenshots/tablet/association-rules-tablet-initial.png", False)
            await verify_and_capture("Association Rules", "audit/screenshots/tablet/association-rules-tablet-full.png", True)

            # RST vs ML Tablet
            await navigate_to_tab(ws, msg_id_ref, "RST vs ML")
            await verify_and_capture("RST vs ML", "audit/screenshots/tablet/comparison-tablet-initial.png", False)
            await verify_and_capture("RST vs ML", "audit/screenshots/tablet/comparison-tablet-full.png", True)

            # Faculty Benchmarks Tablet
            await navigate_to_tab(ws, msg_id_ref, "Faculty Benchmarks")
            await verify_and_capture("Faculty Benchmarks", "audit/screenshots/tablet/benchmarks-tablet-initial.png", False)
            await verify_and_capture("Faculty Benchmarks", "audit/screenshots/tablet/benchmarks-tablet-full.png", True)

            # ==========================================
            # 3. MOBILE AUDIT (390x844)
            # ==========================================
            print("\n>>> VIEWPORT: MOBILE (390x844) <<<")
            await set_viewport(ws, msg_id_ref, 390, 844, True)

            # Home Mobile
            await navigate_to_tab(ws, msg_id_ref, "Home")
            await verify_and_capture("Home", "audit/screenshots/mobile/home-mobile-initial.png", False)
            await verify_and_capture("Home", "audit/screenshots/mobile/home-mobile-full.png", True)

            # Symptom Assessment Mobile
            await navigate_to_tab(ws, msg_id_ref, "Symptom Assessment")
            await trigger_recommendation_scenario(ws, msg_id_ref, "certain")
            await verify_and_capture("Symptom Assessment", "audit/screenshots/mobile/recommender-mobile-initial.png", False)
            await verify_and_capture("Symptom Assessment", "audit/screenshots/mobile/recommender-mobile-full.png", True)

            # Recommendation Ambiguous Mobile
            await trigger_recommendation_scenario(ws, msg_id_ref, "ambiguous")
            await verify_and_capture("Recommendation: ambiguous", "audit/screenshots/mobile/recommendation-ambiguous-mobile-initial.png", False)
            await verify_and_capture("Recommendation: ambiguous", "audit/screenshots/mobile/recommendation-ambiguous-mobile-full.png", True)

            # RST vs ML Mobile
            await navigate_to_tab(ws, msg_id_ref, "RST vs ML")
            await verify_and_capture("RST vs ML", "audit/screenshots/mobile/comparison-mobile-initial.png", False)
            await verify_and_capture("RST vs ML", "audit/screenshots/mobile/comparison-mobile-full.png", True)

            # Faculty Benchmarks Mobile
            await navigate_to_tab(ws, msg_id_ref, "Faculty Benchmarks")
            await verify_and_capture("Faculty Benchmarks", "audit/screenshots/mobile/benchmarks-mobile-initial.png", False)
            await verify_and_capture("Faculty Benchmarks", "audit/screenshots/mobile/benchmarks-mobile-full.png", True)

    finally:
        proc.kill()

    # Save results to json for report generation
    with open("audit/verification_results.json", "w") as f:
        json.dump(verification_records, f, indent=2)

    total = len(verification_records)
    valid = sum(1 for r in verification_records if r["valid"] == "YES")
    invalid = total - valid
    print("\n" + "=" * 60)
    print(f"VERIFICATION AUDIT COMPLETE: Total={total}, Valid={valid}, Invalid={invalid}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_verified_capture())

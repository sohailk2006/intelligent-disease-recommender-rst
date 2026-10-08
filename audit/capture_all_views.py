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
OUTPUT_DIR = "audit/screenshots_final"

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
    filepath = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(img_data)
    print(f"Captured: {filepath} ({len(img_data)} bytes)")

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
        await evaluate(ws, msg_id, """
            (() => {
                let drawer = document.getElementById('mobile-menu-drawer');
                if (!drawer) {
                    const btn = document.getElementById('mobile-menu-btn') ||
                                document.querySelector('button[aria-label="Toggle Navigation Menu"]');
                    if (btn) btn.click();
                }
            })()
        """)
        await asyncio.sleep(0.3)
        await evaluate(ws, msg_id, f"""
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
        await evaluate(ws, msg_id, f"""
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
    await asyncio.sleep(0.8)

async def check_no_horizontal_overflow(ws, msg_id):
    res = await evaluate(ws, msg_id, """
        (() => {
            const scrollW = document.documentElement.scrollWidth;
            const clientW = document.documentElement.clientWidth;
            return scrollW <= clientW + 2; // allowance of 2px for subpixel
        })()
    """)
    return bool(res)

async def run_full_capture():
    print("Launching Chrome for complete screenshot coverage...")
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

        async with websockets.connect(ws_url, max_size=30_000_000) as ws:
            msg_id = 1
            await send_cmd(ws, msg_id, "Page.enable"); msg_id += 1
            await send_cmd(ws, msg_id, "DOM.enable"); msg_id += 1
            await send_cmd(ws, msg_id, "Runtime.enable"); msg_id += 1
            await asyncio.sleep(1.5)

            report = {}

            # ================================================================
            # VIEWPORT 1: Desktop 1920x1080
            # ================================================================
            print("\n=== VIEWPORT: Desktop 1920x1080 ===")
            await set_viewport(ws, msg_id, 1920, 1080, False); msg_id += 1
            await send_cmd(ws, msg_id, "Page.navigate", {"url": TARGET_URL}); msg_id += 1
            await asyncio.sleep(1.5)
            await capture(ws, msg_id, "1920x1080_01_overview.png"); msg_id += 1
            report["desktop_1920_no_overflow"] = await check_no_horizontal_overflow(ws, msg_id); msg_id += 1

            # Assessment Fresh
            await navigate_tab(ws, msg_id, "recommender"); msg_id += 1
            await capture(ws, msg_id, "1920x1080_02_assessment_fresh.png"); msg_id += 1

            # Recommendation Certain (Dengue Complete)
            await evaluate(ws, msg_id, """
                (() => {
                    const btn = document.querySelector('button[data-preset-id="dengue_complete"]');
                    if (btn) btn.click();
                })()
            """); msg_id += 1
            await asyncio.sleep(1.0)
            await capture(ws, msg_id, "1920x1080_04_recommendation_certain.png"); msg_id += 1

            # RST vs ML
            await navigate_tab(ws, msg_id, "comparison"); msg_id += 1
            await capture(ws, msg_id, "1920x1080_07_rst_vs_ml.png"); msg_id += 1

            # RST Theory
            await navigate_tab(ws, msg_id, "rst_theory"); msg_id += 1
            await capture(ws, msg_id, "1920x1080_09_theory.png"); msg_id += 1

            # Association Rules
            await navigate_tab(ws, msg_id, "rules"); msg_id += 1
            await capture(ws, msg_id, "1920x1080_10_rules.png"); msg_id += 1

            # Benchmarks
            await navigate_tab(ws, msg_id, "benchmarks"); msg_id += 1
            await capture(ws, msg_id, "1920x1080_11_benchmarks.png"); msg_id += 1

            # ================================================================
            # VIEWPORT: Desktop 1440x900 & 1366x768
            # ================================================================
            print("\n=== VIEWPORT: Desktop 1440x900 ===")
            await set_viewport(ws, msg_id, 1440, 900, False); msg_id += 1
            await navigate_tab(ws, msg_id, "home"); msg_id += 1
            await capture(ws, msg_id, "1440x900_overview.png"); msg_id += 1
            report["desktop_1440_no_overflow"] = await check_no_horizontal_overflow(ws, msg_id); msg_id += 1

            print("\n=== VIEWPORT: Desktop 1366x768 ===")
            await set_viewport(ws, msg_id, 1366, 768, False); msg_id += 1
            await navigate_tab(ws, msg_id, "home"); msg_id += 1
            await capture(ws, msg_id, "1366x768_overview.png"); msg_id += 1
            report["desktop_1366_no_overflow"] = await check_no_horizontal_overflow(ws, msg_id); msg_id += 1

            # ================================================================
            # VIEWPORT 2: Tablet 1024x768
            # ================================================================
            print("\n=== VIEWPORT: Tablet 1024x768 ===")
            await set_viewport(ws, msg_id, 1024, 768, False); msg_id += 1
            await send_cmd(ws, msg_id, "Page.navigate", {"url": TARGET_URL}); msg_id += 1
            await asyncio.sleep(1.5)
            await capture(ws, msg_id, "1024x768_overview.png"); msg_id += 1
            report["tablet_1024_no_overflow"] = await check_no_horizontal_overflow(ws, msg_id); msg_id += 1

            # Tablet Assessment
            await navigate_tab(ws, msg_id, "recommender"); msg_id += 1
            await capture(ws, msg_id, "1024x768_assessment.png"); msg_id += 1

            # Tablet Recommendation (Dengue Complete)
            await evaluate(ws, msg_id, """
                (() => {
                    const btn = document.querySelector('button[data-preset-id="dengue_complete"]');
                    if (btn) btn.click();
                })()
            """); msg_id += 1
            await asyncio.sleep(1.0)
            await capture(ws, msg_id, "1024x768_recommendation.png"); msg_id += 1

            # Tablet RST Theory
            await navigate_tab(ws, msg_id, "rst_theory"); msg_id += 1
            await capture(ws, msg_id, "1024x768_rst_theory.png"); msg_id += 1

            # Tablet Association Rules
            await navigate_tab(ws, msg_id, "rules"); msg_id += 1
            await capture(ws, msg_id, "1024x768_rules.png"); msg_id += 1

            # Tablet RST vs ML
            await navigate_tab(ws, msg_id, "comparison"); msg_id += 1
            await capture(ws, msg_id, "1024x768_rst_vs_ml.png"); msg_id += 1

            # Tablet Benchmarks
            await navigate_tab(ws, msg_id, "benchmarks"); msg_id += 1
            await capture(ws, msg_id, "1024x768_benchmarks.png"); msg_id += 1

            # ================================================================
            # VIEWPORT 3: Mobile 390x844
            # ================================================================
            print("\n=== VIEWPORT: Mobile 390x844 ===")
            await set_viewport(ws, msg_id, 390, 844, True); msg_id += 1
            await send_cmd(ws, msg_id, "Page.navigate", {"url": TARGET_URL}); msg_id += 1
            await asyncio.sleep(1.5)
            await capture(ws, msg_id, "390x844_overview.png"); msg_id += 1
            report["mobile_390_no_overflow"] = await check_no_horizontal_overflow(ws, msg_id); msg_id += 1

            # Mobile Drawer Open Check
            await evaluate(ws, msg_id, """
                (() => {
                    const btn = document.getElementById('mobile-menu-btn');
                    if (btn) btn.click();
                })()
            """); msg_id += 1
            await asyncio.sleep(0.4)
            await capture(ws, msg_id, "390x844_02_drawer_open.png"); msg_id += 1

            # Mobile Assessment (Fresh)
            await navigate_tab(ws, msg_id, "recommender", is_mobile=True); msg_id += 1
            await capture(ws, msg_id, "390x844_assessment.png"); msg_id += 1

            # Mobile Recommendation Certain (Dengue Complete)
            await evaluate(ws, msg_id, """
                (() => {
                    const btn = document.querySelector('button[data-preset-id="dengue_complete"]');
                    if (btn) btn.click();
                })()
            """); msg_id += 1
            await asyncio.sleep(1.0)
            await capture(ws, msg_id, "390x844_recommendation_certain.png"); msg_id += 1

            # Mobile Recommendation Ambiguous (Dengue 70% Missing)
            # Re-expand editor and click Dengue 70% missing
            await evaluate(ws, msg_id, """
                (() => {
                    const editBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Edit Symptoms'));
                    if (editBtn) editBtn.click();
                })()
            """); msg_id += 1
            await asyncio.sleep(0.4)
            await evaluate(ws, msg_id, """
                (() => {
                    const btn = document.querySelector('button[data-preset-id="dengue_70_missing"]');
                    if (btn) btn.click();
                })()
            """); msg_id += 1
            await asyncio.sleep(1.0)
            await capture(ws, msg_id, "390x844_recommendation_ambiguous.png"); msg_id += 1

            # Mobile RST Theory
            await navigate_tab(ws, msg_id, "rst_theory", is_mobile=True); msg_id += 1
            await capture(ws, msg_id, "390x844_rst_theory.png"); msg_id += 1

            # Mobile Association Rules
            await navigate_tab(ws, msg_id, "rules", is_mobile=True); msg_id += 1
            await capture(ws, msg_id, "390x844_rules.png"); msg_id += 1

            # Mobile RST vs ML
            await navigate_tab(ws, msg_id, "comparison", is_mobile=True); msg_id += 1
            await capture(ws, msg_id, "390x844_rst_vs_ml.png"); msg_id += 1

            # Mobile Benchmarks
            await navigate_tab(ws, msg_id, "benchmarks", is_mobile=True); msg_id += 1
            await capture(ws, msg_id, "390x844_benchmarks.png"); msg_id += 1

            # ================================================================
            # VIEWPORT 4: Mobile 360x800
            # ================================================================
            print("\n=== VIEWPORT: Mobile 360x800 ===")
            await set_viewport(ws, msg_id, 360, 800, True); msg_id += 1
            await send_cmd(ws, msg_id, "Page.navigate", {"url": TARGET_URL}); msg_id += 1
            await asyncio.sleep(1.5)
            await capture(ws, msg_id, "360x800_overview.png"); msg_id += 1
            report["mobile_360_no_overflow"] = await check_no_horizontal_overflow(ws, msg_id); msg_id += 1

            # Mobile 360 Assessment
            await navigate_tab(ws, msg_id, "recommender", is_mobile=True); msg_id += 1
            await capture(ws, msg_id, "360x800_assessment.png"); msg_id += 1

            # Mobile 360 Recommendation Ambiguous (Malaria 70% Missing)
            await evaluate(ws, msg_id, """
                (() => {
                    const btn = document.querySelector('button[data-preset-id="malaria_70_missing"]') ||
                                document.querySelector('button[data-preset-id="dengue_70_missing"]');
                    if (btn) btn.click();
                })()
            """); msg_id += 1
            await asyncio.sleep(1.0)
            await capture(ws, msg_id, "360x800_recommendation_ambiguous.png"); msg_id += 1

            # Mobile 360 RST Theory
            await navigate_tab(ws, msg_id, "rst_theory", is_mobile=True); msg_id += 1
            await capture(ws, msg_id, "360x800_rst_theory.png"); msg_id += 1

            # Mobile 360 Association Rules
            await navigate_tab(ws, msg_id, "rules", is_mobile=True); msg_id += 1
            await capture(ws, msg_id, "360x800_rules.png"); msg_id += 1

            # Mobile 360 RST vs ML
            await navigate_tab(ws, msg_id, "comparison", is_mobile=True); msg_id += 1
            await capture(ws, msg_id, "360x800_rst_vs_ml.png"); msg_id += 1

            # Mobile 360 Benchmarks
            await navigate_tab(ws, msg_id, "benchmarks", is_mobile=True); msg_id += 1
            await capture(ws, msg_id, "360x800_benchmarks.png"); msg_id += 1

            # Save report
            with open("audit/full_coverage_report.json", "w") as f:
                json.dump(report, f, indent=2)
            print("\nFull screenshot coverage successfully completed! Report saved to audit/full_coverage_report.json")

    finally:
        proc.kill()

if __name__ == "__main__":
    asyncio.run(run_full_capture())

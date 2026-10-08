import asyncio
import json
import os
import subprocess
import time
import base64
import requests
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
REMOTE_PORT = 9222
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

async def run_audit():
    # Start Chrome with remote debugging
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
        # Get websocket debugger URL
        tabs = requests.get(f"http://localhost:{REMOTE_PORT}/json").json()
        target_tab = next(t for t in tabs if t.get("type") == "page")
        ws_url = target_tab["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url, max_size=20_000_000) as ws:
            msg_id = 1
            await send_cmd(ws, msg_id, "Page.enable"); msg_id += 1
            await send_cmd(ws, msg_id, "DOM.enable"); msg_id += 1
            await send_cmd(ws, msg_id, "Runtime.enable"); msg_id += 1

            # Wait for app to mount
            await asyncio.sleep(2)

            # ==========================================
            # 1. DESKTOP AUDIT (1920x1080)
            # ==========================================
            print("\n--- DESKTOP CAPTURES (1920x1080) ---")
            await set_viewport(ws, msg_id, 1920, 1080, False); msg_id += 1

            # HOME PAGE
            await evaluate(ws, msg_id, "window.scrollTo(0,0)"); msg_id += 1
            await asyncio.sleep(0.5)
            await capture(ws, msg_id, "audit/screenshots/desktop/home-desktop-initial.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/desktop/home-desktop-full.png", True); msg_id += 1
            await evaluate(ws, msg_id, "window.scrollTo(0, document.body.scrollHeight)"); msg_id += 1
            await asyncio.sleep(0.5)
            await capture(ws, msg_id, "audit/screenshots/desktop/home-desktop-bottom.png", False); msg_id += 1

            # NAVIGATE TO RECOMMENDER
            await evaluate(ws, msg_id, """
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Symptom Assessment'));
                if (btn) btn.click();
            """); msg_id += 1
            await asyncio.sleep(1)
            await evaluate(ws, msg_id, "window.scrollTo(0,0)"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/desktop/recommender-desktop-default.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/desktop/recommender-desktop-full.png", True); msg_id += 1

            # TEST SCENARIO A: Complete Dengue (Already loaded or click Preset)
            await evaluate(ws, msg_id, """
                const p1 = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Dengue') && b.textContent.includes('0%'));
                if (p1) p1.click();
            """); msg_id += 1
            await asyncio.sleep(1.5)
            await capture(ws, msg_id, "audit/screenshots/desktop/recommendation-certain-desktop.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/desktop/recommendation-certain-desktop-full.png", True); msg_id += 1

            # TEST SCENARIO B: 50% Unknown Dengue
            await evaluate(ws, msg_id, """
                const p2 = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Dengue') && b.textContent.includes('50%'));
                if (p2) p2.click();
            """); msg_id += 1
            await asyncio.sleep(1.5)
            await capture(ws, msg_id, "audit/screenshots/desktop/recommendation-50pct-desktop.png", False); msg_id += 1

            # TEST SCENARIO C: 1 symptom (Vomiting) - Boundary Ambiguity
            await evaluate(ws, msg_id, """
                const resetBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Set All Unknown'));
                if (resetBtn) resetBtn.click();
                // Set vomiting to Yes
                const rows = Array.from(document.querySelectorAll('tr'));
                const vomRow = rows.find(r => r.textContent.includes('Vomiting'));
                if (vomRow) {
                    const yesBtn = Array.from(vomRow.querySelectorAll('button')).find(b => b.textContent.trim() === 'YES');
                    if (yesBtn) yesBtn.click();
                }
                const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Run Disease Recommendation'));
                if (runBtn) runBtn.click();
            """); msg_id += 1
            await asyncio.sleep(1.5)
            await capture(ws, msg_id, "audit/screenshots/desktop/recommendation-ambiguous-desktop.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/desktop/recommendation-ambiguous-desktop-full.png", True); msg_id += 1

            # TEST SCENARIO D: 132 Unknown (Insufficient Info)
            await evaluate(ws, msg_id, """
                const resetBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Set All Unknown'));
                if (resetBtn) resetBtn.click();
                const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Run Disease Recommendation'));
                if (runBtn) runBtn.click();
            """); msg_id += 1
            await asyncio.sleep(1.5)
            await capture(ws, msg_id, "audit/screenshots/desktop/recommendation-insufficient-info-desktop.png", False); msg_id += 1

            # RST THEORY & REDUCTS TAB
            await evaluate(ws, msg_id, """
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Rough Set & Reducts'));
                if (btn) btn.click();
            """); msg_id += 1
            await asyncio.sleep(1)
            await evaluate(ws, msg_id, "window.scrollTo(0,0)"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/desktop/rst-theory-desktop-initial.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/desktop/rst-theory-desktop-full.png", True); msg_id += 1

            # ASSOCIATION RULES TAB
            await evaluate(ws, msg_id, """
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Association Rules'));
                if (btn) btn.click();
            """); msg_id += 1
            await asyncio.sleep(1)
            await evaluate(ws, msg_id, "window.scrollTo(0,0)"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/desktop/association-rules-desktop-initial.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/desktop/association-rules-desktop-full.png", True); msg_id += 1

            # RST VS ML LAB TAB
            await evaluate(ws, msg_id, """
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('RST vs ML Lab'));
                if (btn) btn.click();
            """); msg_id += 1
            await asyncio.sleep(1)
            await evaluate(ws, msg_id, "window.scrollTo(0,0)"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/desktop/comparison-desktop-initial.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/desktop/comparison-desktop-full.png", True); msg_id += 1

            # Test Missing Rate Switcher (70% Missing)
            await evaluate(ws, msg_id, """
                const r70 = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('70% Missing'));
                if (r70) r70.click();
            """); msg_id += 1
            await asyncio.sleep(0.5)
            await capture(ws, msg_id, "audit/screenshots/desktop/comparison-70pct-missing-desktop.png", False); msg_id += 1

            # FACULTY BENCHMARKS TAB
            await evaluate(ws, msg_id, """
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Faculty Benchmarks'));
                if (btn) btn.click();
            """); msg_id += 1
            await asyncio.sleep(1)
            await evaluate(ws, msg_id, "window.scrollTo(0,0)"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/desktop/benchmarks-desktop-initial.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/desktop/benchmarks-desktop-full.png", True); msg_id += 1

            # ==========================================
            # 2. TABLET AUDIT (1024x768)
            # ==========================================
            print("\n--- TABLET CAPTURES (1024x768) ---")
            await set_viewport(ws, msg_id, 1024, 768, False); msg_id += 1

            # HOME TABLET
            await evaluate(ws, msg_id, """
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Overview'));
                if (btn) btn.click();
            """); msg_id += 1
            await asyncio.sleep(0.5)
            await evaluate(ws, msg_id, "window.scrollTo(0,0)"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/tablet/home-tablet-initial.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/tablet/home-tablet-full.png", True); msg_id += 1

            # RECOMMENDER TABLET
            await evaluate(ws, msg_id, """
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Symptom Assessment'));
                if (btn) btn.click();
            """); msg_id += 1
            await asyncio.sleep(0.5)
            await evaluate(ws, msg_id, "window.scrollTo(0,0)"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/tablet/recommender-tablet-initial.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/tablet/recommender-tablet-full.png", True); msg_id += 1

            # COMPARISON LAB TABLET
            await evaluate(ws, msg_id, """
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('RST vs ML Lab'));
                if (btn) btn.click();
            """); msg_id += 1
            await asyncio.sleep(0.5)
            await evaluate(ws, msg_id, "window.scrollTo(0,0)"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/tablet/comparison-tablet-initial.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/tablet/comparison-tablet-full.png", True); msg_id += 1

            # BENCHMARKS TABLET
            await evaluate(ws, msg_id, """
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Faculty Benchmarks'));
                if (btn) btn.click();
            """); msg_id += 1
            await asyncio.sleep(0.5)
            await evaluate(ws, msg_id, "window.scrollTo(0,0)"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/tablet/benchmarks-tablet-initial.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/tablet/benchmarks-tablet-full.png", True); msg_id += 1

            # ==========================================
            # 3. MOBILE AUDIT (390x844 iPhone 12/13/14)
            # ==========================================
            print("\n--- MOBILE CAPTURES (390x844) ---")
            await set_viewport(ws, msg_id, 390, 844, True); msg_id += 1

            # HOME MOBILE
            await evaluate(ws, msg_id, """
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Overview'));
                if (btn) btn.click();
            """); msg_id += 1
            await asyncio.sleep(0.5)
            await evaluate(ws, msg_id, "window.scrollTo(0,0)"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/mobile/home-mobile-initial.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/mobile/home-mobile-full.png", True); msg_id += 1

            # RECOMMENDER MOBILE
            await evaluate(ws, msg_id, """
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Symptom Assessment'));
                if (btn) btn.click();
            """); msg_id += 1
            await asyncio.sleep(0.5)
            await evaluate(ws, msg_id, "window.scrollTo(0,0)"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/mobile/recommender-mobile-initial.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/mobile/recommender-mobile-full.png", True); msg_id += 1

            # AMBIGUOUS RESULT ON MOBILE
            await evaluate(ws, msg_id, """
                const p4 = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Preset 4'));
                if (p4) p4.click();
            """); msg_id += 1
            await asyncio.sleep(0.5)
            await evaluate(ws, msg_id, """
                const runBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Run Disease Recommendation'));
                if (runBtn) runBtn.click();
            """); msg_id += 1
            await asyncio.sleep(1.5)
            await capture(ws, msg_id, "audit/screenshots/mobile/recommendation-ambiguous-mobile-initial.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/mobile/recommendation-ambiguous-mobile-full.png", True); msg_id += 1

            # COMPARISON LAB MOBILE
            await evaluate(ws, msg_id, """
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('RST vs ML Lab'));
                if (btn) btn.click();
            """); msg_id += 1
            await asyncio.sleep(0.5)
            await evaluate(ws, msg_id, "window.scrollTo(0,0)"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/mobile/comparison-mobile-initial.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/mobile/comparison-mobile-full.png", True); msg_id += 1

            # BENCHMARKS MOBILE
            await evaluate(ws, msg_id, """
                const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Faculty Benchmarks'));
                if (btn) btn.click();
            """); msg_id += 1
            await asyncio.sleep(0.5)
            await evaluate(ws, msg_id, "window.scrollTo(0,0)"); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/mobile/benchmarks-mobile-initial.png", False); msg_id += 1
            await capture(ws, msg_id, "audit/screenshots/mobile/benchmarks-mobile-full.png", True); msg_id += 1

            print("\nALL SCREENSHOTS CAPTURED SUCCESSFULLY!")

    finally:
        proc.terminate()

if __name__ == "__main__":
    asyncio.run(run_audit())

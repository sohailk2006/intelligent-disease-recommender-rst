import asyncio
import json
import os
import subprocess
import time
import base64
import requests
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
REMOTE_PORT = 9225
TARGET_URL = "http://127.0.0.1:5173/"
OUT_DIR = "audit/screenshots_final"

VIEWPORTS = [
    {"name": "mobile_390", "width": 390, "height": 844, "is_mobile": True},
    {"name": "mobile_360", "width": 360, "height": 800, "is_mobile": True},
    {"name": "tablet_1024", "width": 1024, "height": 768, "is_mobile": False},
    {"name": "desktop_1366", "width": 1366, "height": 768, "is_mobile": False},
    {"name": "desktop_1920", "width": 1920, "height": 1080, "is_mobile": False},
]

msg_counter = 1

def next_id():
    global msg_counter
    msg_counter += 1
    return msg_counter

async def send_cmd(ws, method, params=None):
    m_id = next_id()
    payload = {"id": m_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(payload))
    while True:
        resp = await ws.recv()
        data = json.loads(resp)
        if data.get("id") == m_id:
            return data.get("result", {})

async def capture(ws, filename, full_page=False):
    params = {"format": "png"}
    if full_page:
        params["captureBeyondViewport"] = True
    res = await send_cmd(ws, "Page.captureScreenshot", params)
    img_data = base64.b64decode(res["data"])
    filepath = os.path.join(OUT_DIR, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(img_data)
    print(f"Captured: {filepath} ({len(img_data)} bytes)")

async def set_viewport(ws, width, height, is_mobile=False):
    params = {
        "width": width,
        "height": height,
        "deviceScaleFactor": 1,
        "mobile": is_mobile,
    }
    await send_cmd(ws, "Emulation.setDeviceMetricsOverride", params)
    await asyncio.sleep(0.3)

async def evaluate(ws, expression):
    params = {"expression": expression, "awaitPromise": True, "returnByValue": True}
    res = await send_cmd(ws, "Runtime.evaluate", params)
    return res.get("result", {}).get("value")

async def navigate_tab(ws, tab_id, is_mobile=False):
    if is_mobile:
        await evaluate(ws, """
            (() => {
                let drawer = document.getElementById('mobile-menu-drawer');
                if (!drawer) {
                    const btn = document.getElementById('mobile-menu-btn') ||
                                document.querySelector('button[aria-label="Toggle Navigation Menu"]');
                    if (btn) btn.click();
                }
            })()
        """)
        await asyncio.sleep(0.4)
        await evaluate(ws, f"""
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
        await evaluate(ws, f"""
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

async def run():
    print(f"Starting headless Chrome on remote debugging port {REMOTE_PORT}...")
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
            # Enable Runtime to capture console logs
            await send_cmd(ws, "Runtime.enable")
            
            summary = {}

            for vp in VIEWPORTS:
                name = vp["name"]
                w, h = vp["width"], vp["height"]
                is_mob = vp["is_mobile"]
                print(f"\n--- Verifying Viewport: {name} ({w}x{h}) ---")
                await set_viewport(ws, w, h, is_mob)

                vp_res = {"name": name, "width": w, "height": h}

                # 1. Home / Overview
                await navigate_tab(ws, "overview", is_mob)
                await asyncio.sleep(0.5)

                # Check horizontal overflow
                home_overflow = await evaluate(ws, "document.documentElement.scrollWidth > document.documentElement.clientWidth + 2")
                vp_res["home_no_overflow"] = not bool(home_overflow)

                # Check Pawlak badge absence
                pawlak_count = await evaluate(ws, """
                    (() => {
                        const hero = document.querySelector('.glass-panel');
                        if (!hero) return 0;
                        const text = hero.innerText;
                        const matches = text.match(/Pawlak/gi);
                        return matches ? matches.length : 0;
                    })()
                """)
                vp_res["home_pawlak_count"] = pawlak_count

                # Capture Home screenshot
                await capture(ws, f"{w}x{h}_home_signoff.png")

                # 2. Association Rules
                await navigate_tab(ws, "rules", is_mob)
                await asyncio.sleep(0.5)

                rules_overflow = await evaluate(ws, "document.documentElement.scrollWidth > document.documentElement.clientWidth + 2")
                vp_res["rules_no_overflow"] = not bool(rules_overflow)

                # Check slider and label visibility and bounding boxes
                slider_info = await evaluate(ws, """
                    (() => {
                        const slider = document.querySelector('input[type="range"][aria-label="Display confidence threshold"]');
                        const label = Array.from(document.querySelectorAll('span')).find(s => s.innerText.includes('Display confidence ≥'));
                        if (!slider || !label) return { found: false };
                        const sRect = slider.getBoundingClientRect();
                        const lRect = label.getBoundingClientRect();
                        const winW = window.innerWidth;
                        return {
                            found: true,
                            labelText: label.innerText.trim(),
                            labelClipped: lRect.right > winW || lRect.left < 0,
                            sliderClipped: sRect.right > winW || sRect.left < 0,
                            sliderRight: sRect.right,
                            windowWidth: winW
                        };
                    })()
                """)
                vp_res["rules_slider_info"] = slider_info
                await capture(ws, f"{w}x{h}_rules_signoff.png")

                # 3. RST vs ML
                await navigate_tab(ws, "comparison", is_mob)
                await asyncio.sleep(0.5)

                rst_ml_overflow = await evaluate(ws, "document.documentElement.scrollWidth > document.documentElement.clientWidth + 2")
                vp_res["rst_ml_no_overflow"] = not bool(rst_ml_overflow)

                wording_check = await evaluate(ws, """
                    (() => {
                        const text = document.body.innerText;
                        const hasNew = text.includes("RST preserves unknown symptoms as unknown rather than treating them as absent.");
                        const hasOld = text.includes("RST preserves epistemic tolerance");
                        return { has_new_wording: hasNew, has_old_epistemic: hasOld };
                    })()
                """)
                vp_res["rst_ml_wording"] = wording_check
                await capture(ws, f"{w}x{h}_rst_vs_ml_signoff.png")

                summary[name] = vp_res

            print("\n=== VERIFICATION SUMMARY ===")
            print(json.dumps(summary, indent=2))
            with open("audit/final_signoff_verification.json", "w") as f:
                json.dump(summary, f, indent=2)

    finally:
        proc.terminate()

if __name__ == "__main__":
    asyncio.run(run())

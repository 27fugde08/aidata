import asyncio
import sys
import os
import json

# Thêm path để import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from plugins.douyin_viral.main import DouyinViralPlugin

async def run_test():
    # Load manifest
    manifest_path = os.path.join(os.path.dirname(__file__), "manifest.json")
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    print("🤖 [TEST AGENT] Initializing Douyin Viral Plugin Test...")
    plugin = DouyinViralPlugin("test_workspace", manifest)
    
    # 1. Test Setup
    print("🛠️ [TEST] Running Setup...")
    await plugin.setup()
    
    # 2. Test Scan
    print("📡 [TEST] Running Viral Scan...")
    scan_result = await plugin.execute({"action": "scan"})
    print(f"   Scan Result: {scan_result['status']} (Candidates: {len(scan_result.get('candidates', []))})")
    
    if not scan_result.get("candidates"):
        print("❌ [TEST] Scan failed to find candidates.")
        return

    target = scan_result['candidates'][0]
    
    # 3. Test Download
    print(f"⬇️ [TEST] Downloading target: {target['title']}...")
    dl_result = await plugin.execute({"action": "download", "url": target['url']})
    print(f"   Download Result: {dl_result['status']} -> {dl_result.get('filename', 'N/A')}")
    
    # 4. Test Process
    if dl_result['status'] == "success":
        print("⚙️ [TEST] Processing video...")
        proc_result = await plugin.execute({"action": "process", "filename": dl_result['filename']})
        print(f"   Process Result: {proc_result['status']} -> {proc_result.get('output_path', 'N/A')}")
        
    print("✅ [TEST] Sequence Completed.")

if __name__ == "__main__":
    asyncio.run(run_test())

#!/usr/bin/env python3
"""
tunnel.py — 自由职业者工具 公网隧道
自动尝试多种方式将 localhost:9000 暴露到公网
"""
import os, sys, subprocess, time, json, urllib.request, urllib.error

TUNNEL_SCRIPT = os.path.expanduser("~/freelancer-tool/")

def try_serveo():
    """SSH reverse tunnel via serveo.net"""
    print("[tunnel] Trying serveo.net...")
    import socket
    try:
        socket.setdefaulttimeout(5)
        socket.gethostbyname('serveo.net')
    except:
        print("[tunnel]   serveo.net unreachable, skip")
        return None
    proc = subprocess.Popen(
        ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ServerAliveInterval=30",
         "-R", "80:localhost:9000", "serveo.net"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    time.sleep(5)
    out = ""
    for _ in range(10):  # wait max 10s for URL
        try:
            out += proc.communicate(timeout=1)[0] or ""
        except subprocess.TimeoutExpired:
            pass
        if "serveousercontent" in out or "serveo.net" in out:
            # Extract URL
            for line in out.split('\n'):
                if 'http' in line and 'serveo' in line:
                    url = line.strip().split('http')[1].split()[0]
                    url = 'http' + url
                    print(f"[tunnel] ✅ Serveo: {url}")
                    return url
    print(f"[tunnel]   Serveo output: {out[:200]}")
    return None

def try_localtunnel():
    """lt via npm"""
    print("[tunnel] Trying localtunnel (npm)...")
    try:
        subprocess.run(["npx", "lt", "--version"], capture_output=True, timeout=10)
    except:
        print("[tunnel]   localtunnel not available")
        return None
    try:
        result = subprocess.run(
            ["npx", "lt", "--port", "9000"],
            capture_output=True, text=True, timeout=15
        )
        out = result.stdout + result.stderr
        print(f"[tunnel]   Output: {out[:200]}")
        for line in out.split('\n'):
            if 'url' in line.lower() or 'https://' in line:
                url = line.strip()
                print(f"[tunnel] ✅ localtunnel: {url}")
                return url
    except subprocess.TimeoutExpired:
        pass
    return None

def main():
    print("=" * 50)
    print("  Eve 自由职业者工具 — 公网隧道启动器")
    print("  localhost:9000 → 公网URL")
    print("=" * 50)
    print()

    # Check server is running
    try:
        r = urllib.request.urlopen("http://localhost:9000/", timeout=3)
        if r.status == 200:
            print("[tunnel] ✅ Server on localhost:9000 is running")
        else:
            print("[tunnel] ⚠️  Server responded {r.status}")
    except Exception as e:
        print(f"[tunnel] ❌ Server unreachable: {e}")
        print("[tunnel] Start server first: cd ~/freelancer-tool && python3 -m uvicorn main:app --host 0.0.0.0 --port 9000")
        sys.exit(1)

    # Try tunnels
    url = try_localtunnel() or try_serveo()

    if url:
        print()
        print(f"🎉 公网URL: {url}")
        print(f"   分享给用户: {url}")
        print()
        # Save URL
        with open(os.path.expanduser("~/freelancer-tool/.public_url"), 'w') as f:
            f.write(url)
        # Keep running
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n[tunnel] Tunnel stopped")
    else:
        print()
        print("❌ 所有隧道方式均失败")
        print()
        print("替代方案:")
        print("  1. Windows浏览器: http://localhost:9000")
        print("  2. 运行 deploy_windows.bat (在Windows上)")
        print("  3. 手动: cloudflared tunnel --url http://localhost:9000")

if __name__ == "__main__":
    main()

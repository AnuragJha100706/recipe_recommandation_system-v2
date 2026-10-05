import os
import sys
import time
import webbrowser
import threading
import subprocess
import requests

SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server", "app_cosine_similarity.py")
CLIENT_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "client", "recipe_recommender.html")

def wait_for_server(url="http://127.0.0.1:5000/api/health", timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=1)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.3)
    return False

def main():
    print("==================================================")
    print("      Smart Recipe Recommender - App Launcher     ")
    print("==================================================")
    print("[*] Starting Flask backend server on http://localhost:5000...")
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    server_process = subprocess.Popen([sys.executable, SERVER_SCRIPT], cwd=project_dir)
    
    print("[*] Waiting for backend to initialize dataset and model...")
    is_healthy = wait_for_server()
    if is_healthy:
        print("[*] Backend is UP and HEALTHY!")
        client_url = "http://localhost:5000"
    else:
        print("[!] Backend startup took longer than expected, opening local file fallback...")
        client_url = f"file:///{os.path.abspath(CLIENT_HTML).replace(os.sep, '/')}"
        
    print(f"[*] Opening client interface in browser: {client_url}")
    webbrowser.open(client_url)
    
    print("\n[+] App is running! Press Ctrl+C in this terminal to stop the server.\n")
    try:
        server_process.wait()
    except KeyboardInterrupt:
        print("\n[*] Stopping server...")
        server_process.terminate()
        server_process.wait()
        print("[*] Server stopped. Goodbye!")

if __name__ == "__main__":
    main()

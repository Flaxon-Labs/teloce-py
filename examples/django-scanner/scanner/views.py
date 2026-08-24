import ipaddress
import json
import socket
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from django.http import JsonResponse
from django.shortcuts import render

def home(request):
    return render(request, "index.html")

def _safe_target(value):
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only an absolute HTTP(S) URL is accepted.")
    address = socket.gethostbyname(parsed.hostname)
    if ipaddress.ip_address(address).is_private or ipaddress.ip_address(address).is_loopback:
        raise ValueError("Private and loopback targets are disabled in this demo.")
    return parsed.geturl()

def scan(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        payload = json.loads(request.body or "{}")
        target = _safe_target(str(payload.get("url", "")))
        response = urlopen(Request(target, headers={"User-Agent": "Teloce-Demo-Scanner/1.0"}), timeout=5)
        headers = {key.lower(): value for key, value in response.headers.items()}
        expected = ["content-security-policy", "strict-transport-security", "x-content-type-options", "x-frame-options", "referrer-policy"]
        return JsonResponse({"url": target, "status": response.status, "server": headers.get("server", "hidden"), "findings": [{"header": name, "present": name in headers} for name in expected]})
    except Exception as error:
        return JsonResponse({"error": str(error)}, status=400)

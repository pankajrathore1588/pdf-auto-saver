from flask import Flask, render_template, request, jsonify, send_from_directory
from pathlib import Path
from urllib.parse import urlparse, unquote
from datetime import datetime
from playwright.async_api import async_playwright
import asyncio, threading, uuid, re, hashlib, json

app=Flask(__name__)
BASE=Path(__file__).resolve().parent
SESSION_DIR=BASE/"session_pdfs"; SESSION_DIR.mkdir(exist_ok=True)
browser_loop=None; browser_ready=threading.Event(); browser_thread=None
context=None; main_page=None; session_dir=None; pdf_index=0
seen_hashes=set(); lock=threading.Lock()

def safe_name(url,i):
    n=unquote(Path(urlparse(url).path).name) or "document.pdf"
    n=re.sub(r"[^A-Za-z0-9._-]","_",n)
    if not n.lower().endswith(".pdf"): n+=".pdf"
    return f"{i:03d}_{n}"

async def capture(response):
    global pdf_index
    try:
        h=await response.all_headers()
        c=(h.get("content-type") or "").lower()
        u=response.url
        if "application/pdf" not in c and not urlparse(u).path.lower().endswith(".pdf"): return
        body=await response.body()
        if not body.startswith(b"%PDF"): return
        digest=hashlib.sha256(body).hexdigest()
        with lock:
            if digest in seen_hashes: return
            seen_hashes.add(digest); pdf_index+=1; i=pdf_index
            folder=session_dir
        name=safe_name(u,i); target=folder/name
        await asyncio.to_thread(target.write_bytes,body)
        print(f"[PDF {i:03d}] AUTO-SAVED -> {target}",flush=True)
    except Exception as e: print("[PDF CAPTURE ERROR]",e,flush=True)

def attach(page):
    page.on("response",lambda r:asyncio.create_task(capture(r)))
    print("[BROWSER] listener attached:",page.url,flush=True)

async def worker():
    global browser_loop,context,main_page,session_dir,pdf_index
    browser_loop=asyncio.get_running_loop()
    stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir=SESSION_DIR/f"session_{stamp}_{uuid.uuid4().hex[:6]}"
    session_dir.mkdir(parents=True,exist_ok=True)
    pdf_index=0; seen_hashes.clear()
    profile=BASE/f"browser_profile_{stamp}_{uuid.uuid4().hex[:6]}"
    async with async_playwright() as pw:
        context=await pw.chromium.launch_persistent_context(
            str(profile),headless=False,accept_downloads=True,
            args=["--no-sandbox"],viewport={"width":1400,"height":900})
        context.on("page",attach)
        main_page=await context.new_page(); attach(main_page)
        browser_ready.set()
        print("[BROWSER] Ready.",flush=True)
        await asyncio.Event().wait()

def start_browser():
    global browser_thread
    if browser_thread and browser_thread.is_alive(): return
    browser_thread=threading.Thread(target=lambda:asyncio.run(worker()),daemon=True)
    browser_thread.start()
    if not browser_ready.wait(30): raise RuntimeError("Browser failed to start")

async def goto(url):
    await main_page.goto(url,wait_until="domcontentloaded",timeout=60000)

@app.get("/")
def index(): return render_template("index.html")

@app.post("/api/open")
def open_page():
    url=((request.get_json(silent=True) or {}).get("url") or "").strip()
    if not url.startswith(("http://","https://")): return jsonify(error="Enter a valid http/https URL."),400
    try:
        start_browser()
        asyncio.run_coroutine_threadsafe(goto(url),browser_loop).result(70)
        return jsonify(ok=True,message="Browser opened. Login normally; every PDF is saved automatically.")
    except Exception as e: return jsonify(error=str(e)),500

@app.get("/api/status")
def status(): return jsonify(browser_ready=browser_ready.is_set(),browser_alive=bool(browser_thread and browser_thread.is_alive()))

@app.get("/api/session")
def files():
    if not session_dir or not session_dir.exists(): return jsonify(items=[],count=0)
    a=[{"filename":p.name,"size":p.stat().st_size,"url":"/session-file/"+p.name} for p in sorted(session_dir.glob("*.pdf"))]
    return jsonify(items=a,count=len(a))

@app.get("/session-file/<path:name>")
def file(name):
    if not session_dir:return "No active session",404
    return send_from_directory(session_dir,name,as_attachment=True)

if __name__=="__main__":
    start_browser()
    app.run(host="0.0.0.0",port=8000,debug=False,threaded=True,use_reloader=False)

# 📚 PDF Auto Saver

A Python Flask + Playwright automation tool that monitors PDF responses in an authenticated browser session and automatically saves accessible PDF documents locally in sequential order.

> **Use only with websites and documents you are authorized to access.** This project does not bypass DRM, paywalls, authentication controls, or technical download restrictions.

## ✨ Features
- 🔐 Login once in Chromium
- 📄 Automatically captures normal PDF network responses
- 🔢 Sequential filenames: `001_document.pdf`, `002_document.pdf`, `003_document.pdf`
- 🧠 SHA-256 duplicate-content detection
- 🌐 Flask web dashboard
- 📊 Live saved-PDF counter
- 🖥️ Playwright persistent browser context
- 🔄 Background asyncio event loop
- 📁 Separate session folders

## 🏗️ Architecture

```text
Flask Dashboard → Playwright Chromium → PDF Network Response → Capture Engine → session_pdfs/
```

## 🛠️ Tech Stack
Python 3 · Flask · Playwright · Chromium · asyncio · threading · HTML/CSS/JavaScript · Linux/WSL

## 📂 Project Structure

```text
pdf-saver/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
├── session_pdfs/          # runtime output - ignored by Git
├── saved_pdfs/            # runtime output - ignored by Git
├── browser_profile_*/     # browser data - ignored by Git
└── README.md
```

## 🚀 Local Setup

```bash
git clone https://github.com/YOUR-USERNAME/pdf-auto-saver.git
cd pdf-auto-saver
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
python app.py
```

Open `http://localhost:8000`.

## ▶️ Usage

1. Start the application.
2. Enter an authorized website URL.
3. Click **Open Website in Browser**.
4. Log in normally.
5. Open accessible PDFs normally.
6. PDFs are automatically captured and saved sequentially.

Example:

```text
session_pdfs/session_.../
├── 001_document.pdf
├── 002_notes.pdf
└── 003_assignment.pdf
```

## 🔒 Security & Responsible Use

Never commit passwords, API keys, cookies, browser profiles, session data, downloaded/private documents, or `.env` files. Only use this application for content you are permitted to download or archive.

## ⚠️ Limitations

The application captures PDF content delivered to the browser as a normal accessible PDF response. It is not designed to bypass DRM, encryption, authentication, paywalls, or anti-download mechanisms.

## 🧪 Project Purpose

This project demonstrates Python, Flask, browser automation, Playwright, asynchronous programming, threading, HTTP/network response handling, file handling, SHA-256 hashing, Linux/WSL, and Git/GitHub.

## 👨‍💻 Author

**Pankaj Rathore** — DevOps / Cloud learner with hands-on experience in Linux, AWS, Docker, Kubernetes, Terraform, Jenkins and automation.

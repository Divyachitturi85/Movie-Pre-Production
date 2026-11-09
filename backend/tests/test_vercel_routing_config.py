import json
import re
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

def test_frontend_vercel_json_configuration():
    fpath = REPO_ROOT / "frontend" / "vercel.json"
    assert fpath.exists(), "frontend/vercel.json must exist"
    
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    rewrites = data.get("rewrites", [])
    assert len(rewrites) >= 2, "frontend/vercel.json must contain at least 2 rewrite rules"
    
    # 1. API proxy rule
    api_rule = next((r for r in rewrites if r.get("source") == "/api/:path*"), None)
    assert api_rule is not None, "API rewrite rule /api/:path* missing in frontend/vercel.json"
    assert api_rule["destination"] == "https://movie-pre-production-gi77.onrender.com/api/:path*"
    
    # 2. SPA fallback rule
    spa_rule = next((r for r in rewrites if "index.html" in r.get("destination", "")), None)
    assert spa_rule is not None, "SPA fallback rule missing in frontend/vercel.json"
    assert spa_rule["destination"] == "/index.html"
    assert "api" in spa_rule["source"], "SPA fallback must exclude /api requests from index.html rewrite"

def test_root_vercel_json_matches_frontend():
    root_path = REPO_ROOT / "vercel.json"
    front_path = REPO_ROOT / "frontend" / "vercel.json"
    
    assert root_path.exists(), "root vercel.json must exist"
    assert front_path.exists(), "frontend/vercel.json must exist"
    
    with open(root_path, "r", encoding="utf-8") as f1, open(front_path, "r", encoding="utf-8") as f2:
        root_data = json.load(f1)
        front_data = json.load(f2)
        
    assert root_data == front_data, "root vercel.json and frontend/vercel.json must be identical"

def test_frontend_api_service_production_fallback_url():
    api_service_path = REPO_ROOT / "frontend" / "src" / "services" / "api.js"
    assert api_service_path.exists(), "frontend/src/services/api.js must exist"
    
    with open(api_service_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Must contain live Render backend URL as fallback
    assert "https://movie-pre-production-gi77.onrender.com/api" in content
    # Must NOT contain old dead Render backend URL anywhere
    assert "movie-pre-production.onrender.com" not in content

def test_upload_page_contains_missing_project_user_feedback():
    upload_page_path = REPO_ROOT / "frontend" / "src" / "pages" / "UploadScriptPage.jsx"
    assert upload_page_path.exists(), "UploadScriptPage.jsx must exist"
    
    with open(upload_page_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check that handleUpload gives feedback when currentProject is missing
    assert "No active project selected" in content

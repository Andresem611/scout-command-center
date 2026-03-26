"""
Scout API Server
FastAPI backend for Scout Command Center
Handles data storage and communication between Streamlit app and Scout agent
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime
from pathlib import Path

app = FastAPI(title="Scout API", version="1.0")

# CORS for Streamlit app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data file path
DATA_FILE = Path("scout_data.json")

def load_data():
    """Load data from JSON file"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        "prospects": [],
        "replies": [],
        "interactions": [],
        "blog_forms": [],
        "stats": {
            "total_prospects": 0,
            "contacted": 0,
            "replied": 0,
            "negotiating": 0,
            "live": 1
        }
    }

def save_data(data):
    """Save data to JSON file"""
    data['metadata'] = {
        'last_updated': datetime.now().isoformat(),
        'version': '1.0'
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    return data

# Pydantic models
class Prospect(BaseModel):
    id: str
    name: str
    handle: Optional[str] = ""
    platform: str
    city: str
    branch: str
    followers: Optional[str] = ""
    email: Optional[str] = ""
    score: int
    stage: str = "Prospected"
    notes: Optional[str] = ""
    personalization: Optional[str] = ""
    draft_status: str = "pending"
    last_contact: Optional[str] = None
    next_followup: Optional[str] = None

class ApproveRequest(BaseModel):
    ids: List[str]

class ProspectUpdate(BaseModel):
    stage: Optional[str] = None
    draft_status: Optional[str] = None
    last_contact: Optional[str] = None

class Reply(BaseModel):
    id: str
    from_name: str
    from_email: str
    prospect_id: str
    body: str
    timestamp: str
    urgency: Optional[str] = None
    branch: Optional[str] = None

class BlogForm(BaseModel):
    id: str
    blog_name: str
    url: str
    author_name: Optional[str] = ""
    city: str
    branch: str
    status: str = "manual_needed"
    subject: str
    message: str
    research_notes: Optional[str] = ""

class Interaction(BaseModel):
    id: str
    prospect_name: str
    prospect_id: str
    situation: str
    guidance: str
    response: str
    outcome: str
    pattern_tag: Optional[str] = None

# API Endpoints

@app.get("/")
def root():
    return {"status": "Scout API running", "version": "1.0"}

@app.get("/data")
def get_all_data():
    """Get all data"""
    return load_data()

@app.get("/prospects")
def get_prospects(branch: Optional[str] = None, stage: Optional[str] = None):
    """Get prospects with optional filtering"""
    data = load_data()
    prospects = data.get('prospects', [])
    
    if branch:
        prospects = [p for p in prospects if p.get('branch') == branch]
    if stage:
        prospects = [p for p in prospects if p.get('stage') == stage]
    
    return prospects

@app.get("/prospects/{prospect_id}")
def get_prospect(prospect_id: str):
    """Get a specific prospect"""
    data = load_data()
    prospect = next((p for p in data['prospects'] if p['id'] == prospect_id), None)
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")
    return prospect

@app.post("/prospects")
def add_prospect(prospect: Prospect):
    """Add a new prospect"""
    data = load_data()
    
    # Check for duplicates
    if any(p['id'] == prospect.id for p in data['prospects']):
        raise HTTPException(status_code=400, detail="Prospect ID already exists")
    
    data['prospects'].append(prospect.dict())
    data['stats']['total_prospects'] = len(data['prospects'])
    save_data(data)
    return {"success": True, "prospect": prospect}

@app.post("/prospects/batch")
def add_prospects_batch(prospects: List[Prospect]):
    """Add multiple prospects"""
    data = load_data()
    added = 0
    skipped = 0
    
    for prospect in prospects:
        if any(p['id'] == prospect.id for p in data['prospects']):
            skipped += 1
            continue
        data['prospects'].append(prospect.dict())
        added += 1
    
    data['stats']['total_prospects'] = len(data['prospects'])
    save_data(data)
    return {"success": True, "added": added, "skipped": skipped}

@app.patch("/prospects/{prospect_id}")
def update_prospect(prospect_id: str, update: ProspectUpdate):
    """Update a prospect"""
    data = load_data()
    prospect = next((p for p in data['prospects'] if p['id'] == prospect_id), None)
    
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")
    
    if update.stage:
        prospect['stage'] = update.stage
    if update.draft_status:
        prospect['draft_status'] = update.draft_status
    if update.last_contact:
        prospect['last_contact'] = update.last_contact
    
    # Update stats
    data['stats']['contacted'] = len([p for p in data['prospects'] if p.get('stage') == 'Contacted'])
    data['stats']['replied'] = len([p for p in data['prospects'] if p.get('stage') in ['Replied', 'Negotiating']])
    
    save_data(data)
    return {"success": True, "prospect": prospect}

@app.post("/approve")
def approve_drafts(request: ApproveRequest):
    """Approve drafts for sending"""
    data = load_data()
    approved = []
    
    for prospect_id in request.ids:
        prospect = next((p for p in data['prospects'] if p['id'] == prospect_id), None)
        if prospect and prospect.get('draft_status') == 'pending':
            prospect['draft_status'] = 'approved'
            prospect['approved_at'] = datetime.now().isoformat()
            approved.append(prospect_id)
    
    save_data(data)
    return {
        "success": True, 
        "approved_count": len(approved),
        "approved_ids": approved,
        "message": f"Approved {len(approved)} drafts. Scout will send within 5 minutes."
    }

@app.get("/approved")
def get_approved():
    """Get all approved drafts (for Scout to send)"""
    data = load_data()
    approved = [p for p in data['prospects'] if p.get('draft_status') == 'approved']
    return approved

@app.post("/mark-sent/{prospect_id}")
def mark_sent(prospect_id: str):
    """Mark a prospect as sent (called by Scout after sending)"""
    data = load_data()
    prospect = next((p for p in data['prospects'] if p['id'] == prospect_id), None)
    
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")
    
    prospect['stage'] = 'Contacted'
    prospect['draft_status'] = 'sent'
    prospect['last_contact'] = datetime.now().isoformat()
    
    # Update stats
    data['stats']['contacted'] = len([p for p in data['prospects'] if p.get('stage') == 'Contacted'])
    
    save_data(data)
    return {"success": True}

@app.get("/replies")
def get_replies():
    """Get all replies"""
    data = load_data()
    return data.get('replies', [])

@app.post("/replies")
def add_reply(reply: Reply):
    """Add a new reply (from Scout)"""
    data = load_data()
    data['replies'].append(reply.dict())
    save_data(data)
    return {"success": True, "reply": reply}

@app.get("/blog_forms")
def get_blog_forms(status: Optional[str] = None):
    """Get blog forms"""
    data = load_data()
    forms = data.get('blog_forms', [])
    if status:
        forms = [f for f in forms if f.get('status') == status]
    return forms

@app.post("/blog_forms")
def add_blog_form(form: BlogForm):
    """Add a blog form"""
    data = load_data()
    data['blog_forms'].append(form.dict())
    save_data(data)
    return {"success": True, "form": form}

@app.patch("/blog_forms/{form_id}")
def update_blog_form(form_id: str, update: dict):
    """Update a blog form"""
    data = load_data()
    form = next((f for f in data['blog_forms'] if f['id'] == form_id), None)
    
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    form.update(update)
    save_data(data)
    return {"success": True, "form": form}

@app.get("/interactions")
def get_interactions():
    """Get all interactions"""
    data = load_data()
    return data.get('interactions', [])

@app.post("/interactions")
def add_interaction(interaction: Interaction):
    """Add an interaction"""
    data = load_data()
    data['interactions'].append(interaction.dict())
    save_data(data)
    return {"success": True, "interaction": interaction}

@app.get("/stats")
def get_stats():
    """Get current stats"""
    data = load_data()
    return data.get('stats', {})

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

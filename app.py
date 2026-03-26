import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# Page config
st.set_page_config(
    page_title="Scout Command Center",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark mode and styling
st.markdown("""
<style>
    .main { background-color: #0f0f0f; }
    .stApp { background-color: #0f0f0f; }
    .metric-card { background: #1a1a1a; border: 1px solid #333; border-radius: 12px; padding: 20px; text-align: center; }
    .prospect-card { background: #1a1a1a; border: 1px solid #333; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
    .hot-lead { border-left: 4px solid #ef4444; }
    .pending { border-left: 4px solid #f59e0b; }
    .approved { border-left: 4px solid #22c55e; }
    .stButton > button { width: 100%; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Data file path
DATA_FILE = "scout_data.json"

def load_data():
    """Load data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"prospects": [], "replies": [], "interactions": [], "blog_forms": [], "stats": {}}

def save_data(data):
    """Save data to JSON file"""
    data['metadata'] = {'last_updated': datetime.now().isoformat(), 'version': '1.0'}
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Initialize session state from file
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# Ensure all keys exist
def ensure_keys(data):
    for key in ['prospects', 'replies', 'interactions', 'blog_forms']:
        if key not in data:
            data[key] = []
    if 'stats' not in data:
        data['stats'] = {'total_prospects': 0, 'contacted': 0, 'replied': 0, 'negotiating': 0, 'live': 1}
    return data

st.session_state.data = ensure_keys(st.session_state.data)

# Sidebar navigation
st.sidebar.title("🎯 Scout Command Center")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "☀️ Morning Batch", "📝 Blog Forms", "👥 Pipeline", "📥 Inbox", "🧠 Knowledge Base"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")

# Calculate stats
data = st.session_state.data
total_prospects = len(data['prospects'])
contacted = len([p for p in data['prospects'] if p.get('stage') == 'Contacted'])
replied = len([p for p in data['prospects'] if p.get('stage') in ['Replied', 'Negotiating']])
negotiating = len([p for p in data['prospects'] if p.get('stage') == 'Negotiating'])
live = 1  # Audrey Mora

pending_drafts = len([p for p in data['prospects'] if p.get('draft_status') == 'pending' and p.get('email')])
replies_waiting = len(data['replies'])

st.sidebar.metric("Pipeline", f"{total_prospects}/95")
st.sidebar.metric("Pending Drafts", pending_drafts)
st.sidebar.metric("Replies Waiting", replies_waiting)

# ========== DASHBOARD VIEW ==========
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #888; font-size: 0.9rem;">TOTAL PIPELINE</h3>
            <h1 style="color: #22c55e; font-size: 2.5rem; margin: 10px 0;">{total_prospects}</h1>
            <p style="color: #666;">of 95 target</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #888; font-size: 0.9rem;">CONTACTED THIS WEEK</h3>
            <h1 style="color: #3b82f6; font-size: 2.5rem; margin: 10px 0;">{contacted}</h1>
            <p style="color: #666;">outreach sent</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        reply_rate = f"{(replied/max(contacted,1)*100):.0f}%" if contacted > 0 else "—"
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #888; font-size: 0.9rem;">REPLY RATE</h3>
            <h1 style="color: #f59e0b; font-size: 2.5rem; margin: 10px 0;">{reply_rate}</h1>
            <p style="color: #666;">{replied} replies</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #888; font-size: 0.9rem;">ACTIVE PARTNERS</h3>
            <h1 style="color: #a78bfa; font-size: 2.5rem; margin: 10px 0;">{live}</h1>
            <p style="color: #666;">Audrey Mora</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Branch progress
    st.subheader("📈 Branch Progress")
    
    branches = {
        'Mom Influencers (IG)': (30, len([p for p in data['prospects'] if p.get('branch') == 'Mom Influencers (IG)'])),
        'Mom Influencers (TT/YT)': (15, len([p for p in data['prospects'] if p.get('branch') == 'Mom Influencers (TT/YT)'])),
        'Mom Blogs': (15, len([p for p in data['prospects'] if p.get('branch') == 'Mom Blogs'])),
        'Homeschool Influencers (AZ)': (15, len([p for p in data['prospects'] if p.get('branch') == 'Homeschool Influencers (AZ)'])),
        'Homeschool Blogs (AZ)': (10, len([p for p in data['prospects'] if p.get('branch') == 'Homeschool Blogs (AZ)'])),
        'Homeschool Expansion': (10, len([p for p in data['prospects'] if p.get('branch') == 'Homeschool Expansion']))
    }
    
    for branch, (target, current) in branches.items():
        progress = min(current / target * 100, 100) if target > 0 else 0
        st.progress(progress / 100, text=f"{branch}: {current}/{target}")
    
    st.markdown("---")
    
    # Action items
    st.subheader("⚡ Action Items")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📝 Drafts Pending", pending_drafts)
        if pending_drafts > 0:
            st.info(f"Go to **Morning Batch** to review")
    
    with col2:
        st.metric("💬 Replies Needing Guidance", replies_waiting)
        if replies_waiting > 0:
            st.warning(f"Go to **Inbox** to respond")
    
    with col3:
        manual_forms = len([f for f in data['blog_forms'] if f.get('status') == 'manual_needed'])
        st.metric("📝 Manual Forms", manual_forms)

# ========== MORNING BATCH VIEW ==========
elif page == "☀️ Morning Batch":
    st.title("☀️ Morning Batch")
    st.markdown("Review and approve today's outreach. Approve → I send via AgentMail.")
    st.markdown("---")
    
    # Get prospects with emails that are pending
    pending = [p for p in data['prospects'] 
               if p.get('draft_status') == 'pending' and p.get('email') and p.get('stage') == 'Prospected']
    
    if not pending:
        st.success("🎉 No pending drafts! All caught up.")
        st.info("Scout will queue new prospects here when they're ready for outreach.")
    else:
        st.markdown(f"**{len(pending)} drafts** waiting for approval")
        
        # Approve All button
        if st.button("✅ Approve All", type="primary", use_container_width=True):
            for prospect in pending:
                prospect['draft_status'] = 'approved'
            save_data(data)
            st.success(f"Approved {len(pending)} drafts! Scout will send via AgentMail.")
            st.rerun()
        
        st.markdown("---")
        
        # Draft cards
        for prospect in pending:
            # Generate email body
            email_body = f"""Hi {prospect['name'].split()[0]},

This is Keri! I'm a pianist, music teacher, and co-founder of Thoven — an all-in-one music education platform where families can find verified, background-checked teachers trained at top schools like The Juilliard School.

After years of teaching and working closely with families, I've met so many parents who wanted music lessons for their children but feel unsure where to begin or how to stay connected to their child's progress. That's why we built Thoven.

With Thoven, parents and students can:
- Feel confident knowing every teacher is background-checked and verified
- Seamlessly schedule and pay for lessons in one place (secured with Stripe)
- Access a personalized, gamified dashboard to track progress and motivate practice
- View lesson notes, assignments, and real-time progress updates

We work with a growing group of teachers trained at The Juilliard School, Manhattan School of Music, Eastman School of Music and more.

{prospect.get('personalization', 'I love the way your content connects with your audience')}, so I wanted to reach out personally to see if you'd be open to working together in a way that feels natural for you and your audience.

We'd be happy to structure this in a way that works best for you:
- Affiliate partnership: Earn commission on every lesson booked through your unique link
- Complimentary lessons: We can provide free lessons to your family so you can experience the platform and see the value firsthand
- Other approaches: If you have a preferred method or different structure in mind, we're open to exploring options that work best for you

If you're interested, I'd love to schedule a quick call to walk you through the platform, answer any questions, and explore what a partnership could look like.

If you'd like to learn more, you can find us at Thoven in the meantime —

Looking forward to connecting!

Keri Erten
Co-Founder & CXO
Music Educator & Pianist"""
            
            with st.container():
                st.markdown(f"""
                <div class="prospect-card pending">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h3 style="margin: 0; color: #fff;">{prospect['name']}</h3>
                            <p style="margin: 5px 0; color: #888;">
                                {prospect['branch']} • {prospect['city']} • Score: <b>{prospect['score']}</b>
                            </p>
                            <p style="margin: 5px 0; color: #666; font-size: 0.85rem;">
                                {prospect['handle']} • {prospect['email']}
                            </p>
                        </div>
                        <span style="background: #f59e0b; color: #000; padding: 4px 12px; border-radius: 12px; font-size: 0.8rem;">
                            PENDING
                        </span>
                    </div>
                    <hr style="border-color: #333; margin: 15px 0;">
                    <div style="background: #252525; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <pre style="white-space: pre-wrap; color: #ccc; font-family: inherit; margin: 0; font-size: 0.9rem;">{email_body}</pre>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(f"✅ Approve", key=f"approve_{prospect['id']}", type="primary", use_container_width=True):
                        prospect['draft_status'] = 'approved'
                        save_data(data)
                        st.success(f"Approved: {prospect['name']} — Scout will send")
                        st.rerun()
                
                with col2:
                    if st.button(f"⏭️ Skip", key=f"skip_{prospect['id']}", use_container_width=True):
                        prospect['draft_status'] = 'skipped'
                        save_data(data)
                        st.info(f"Skipped: {prospect['name']}")
                        st.rerun()
                
                st.markdown("---")

# ========== BLOG FORMS VIEW ==========
elif page == "📝 Blog Forms":
    st.title("📝 Blog Forms")
    st.markdown("Contact forms for blogs. Auto-submitted when possible, flagged for manual when blocked.")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_forms = len(data['blog_forms'])
        st.metric("Total Forms", total_forms)
    
    with col2:
        auto_submitted = len([f for f in data['blog_forms'] if f.get('status') == 'auto_submitted'])
        st.metric("✅ Auto-Submitted", auto_submitted)
    
    with col3:
        manual_needed = len([f for f in data['blog_forms'] if f.get('status') == 'manual_needed'])
        st.metric("📝 Manual Needed", manual_needed)
    
    st.markdown("---")
    
    if not data['blog_forms']:
        st.info("No blog forms yet. Scout will add them here when blogs are found without direct email contact.")
    else:
        for form in data['blog_forms']:
            status_color = "#22c55e" if form.get('status') == 'auto_submitted' else "#f59e0b"
            st.markdown(f"""
            <div class="prospect-card" style="border-left: 4px solid {status_color};">
                <h3 style="margin: 0; color: #fff;">{form.get('blog_name', 'Unknown')}</h3>
                <p style="color: #888;">{form.get('url', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)

# ========== PIPELINE VIEW ==========
elif page == "👥 Pipeline":
    st.title("👥 Pipeline")
    
    if data['prospects']:
        df = pd.DataFrame(data['prospects'])
        st.dataframe(df[['name', 'handle', 'city', 'branch', 'score', 'stage', 'email']], use_container_width=True, hide_index=True)
    else:
        st.info("No prospects yet.")

# ========== INBOX VIEW ==========
elif page == "📥 Inbox":
    st.title("📥 Inbox")
    
    if not data['replies']:
        st.info("📭 No replies yet. When prospects respond, they'll appear here.")
    else:
        for reply in data['replies']:
            st.markdown(f"<div class='prospect-card'><h3>{reply.get('from_name', 'Unknown')}</h3></div>", unsafe_allow_html=True)

# ========== KNOWLEDGE BASE VIEW ==========
elif page == "🧠 Knowledge Base":
    st.title("🧠 Knowledge Base")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Interactions", len(data['interactions']))
    
    with col2:
        patterns = set(i.get('pattern_tag', '') for i in data['interactions'] if i.get('pattern_tag'))
        st.metric("Patterns Identified", len(patterns))
    
    with col3:
        st.metric("Response Templates", 0)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(f"<p style='text-align: center; color: #666;'>Scout v1.0 • Last updated: {data.get('metadata', {}).get('last_updated', 'Unknown')[:10]}</p>", unsafe_allow_html=True)

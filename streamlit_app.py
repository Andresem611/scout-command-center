import streamlit as st
import json
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Scout Command Center",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data from shared file
DATA_FILE = "scout_data.json"
APP_VERSION = "1.1.0-agent-panel"  # Cache bust

@st.cache_data(ttl=5)
def load_data():
    """Load data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"prospects": [], "replies": [], "blog_forms": [], "interactions": [], "stats": {}, "agent_status": {}}

def save_data(data):
    """Save data to JSON file"""
    data['metadata'] = {
        'last_updated': datetime.now().isoformat(),
        'version': '1.0'
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    st.cache_data.clear()

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #0f0f0f; }
    .stApp { background-color: #0f0f0f; }
    .metric-card { background: #1a1a1a; border: 1px solid #333; border-radius: 12px; padding: 20px; text-align: center; }
    .prospect-card { background: #1a1a1a; border: 1px solid #333; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
    .prospect-card:hover { border-color: #555; }
    .hot-lead { border-left: 4px solid #ef4444; }
    .pending { border-left: 4px solid #f59e0b; }
    .approved { border-left: 4px solid #22c55e; }
    .sent { border-left: 4px solid #3b82f6; }
    .stButton > button { width: 100%; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Load data
data = load_data()
prospects = data.get('prospects', [])

# Calculate stats
total_prospects = len(prospects)
contacted = len([p for p in prospects if p.get('stage') == 'Contacted'])
replied = len([p for p in prospects if p.get('stage') in ['Replied', 'Negotiating']])
live = 1

pending_drafts = len([p for p in prospects 
                      if p.get('draft_status') == 'pending' 
                      and p.get('email') 
                      and '@' in str(p.get('email', ''))
                      and p.get('stage') == 'Prospected'])

# Sidebar
st.sidebar.title("🎯 Scout Command Center")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "☀️ Morning Batch", "👥 Pipeline", "📥 Inbox", "🧠 Knowledge Base"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")
st.sidebar.metric("Pipeline", f"{total_prospects}/95")
st.sidebar.metric("Pending Approval", pending_drafts)
st.sidebar.metric("Contacted", contacted)

if st.sidebar.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(f"Last updated: {data.get('metadata', {}).get('last_updated', 'Unknown')[:10]}")

# ========== DASHBOARD VIEW ==========
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    
    # DEBUG: Force fresh data load and show if agent_status exists
    st.cache_data.clear()
    data = load_data()
    prospects = data.get('prospects', [])
    
    # Recalculate stats with fresh data
    total_prospects = len(prospects)
    contacted = len([p for p in prospects if p.get('stage') == 'Contacted'])
    replied = len([p for p in prospects if p.get('stage') in ['Replied', 'Negotiating']])
    pending_drafts = len([p for p in prospects 
                          if p.get('draft_status') == 'pending' 
                          and p.get('email') 
                          and '@' in str(p.get('email', ''))
                          and p.get('stage') == 'Prospected'])
    
    # AGENT STATUS PANEL
    agent_status = data.get('agent_status', {})
    last_heartbeat = agent_status.get('last_heartbeat', '')
    current_task = agent_status.get('current_task', 'Unknown')
    status = agent_status.get('status', 'unknown')
    
    # Calculate time since last heartbeat
    time_since = "—"
    status_color = "#ef4444"  # red
    status_dot = "🔴"
    
    if last_heartbeat:
        try:
            last_dt = datetime.fromisoformat(last_heartbeat.replace('Z', '+00:00'))
            now = datetime.now(last_dt.tzinfo) if last_dt.tzinfo else datetime.now()
            diff = (now - last_dt).total_seconds()
            
            if diff < 300:  # < 5 min
                time_since = f"{int(diff//60)}m ago" if diff >= 60 else "Just now"
                status_color = "#22c55e"  # green
                status_dot = "🟢"
            elif diff < 1800:  # < 30 min
                time_since = f"{int(diff//60)}m ago"
                status_color = "#f59e0b"  # yellow
                status_dot = "🟡"
            else:
                time_since = f"{int(diff//3600)}h ago"
                status_color = "#ef4444"  # red
                status_dot = "🔴"
        except:
            time_since = "Unknown"
    
    # Agent status card
    st.markdown(f"""
    <div style="background: #1a1a1a; border: 1px solid #333; border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 4px solid {status_color};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0; color: #fff;">🤖 Scout Agent {status_dot}</h3>
                <p style="margin: 5px 0 0 0; color: #888;">Last seen: <span style="color: {status_color};">{time_since}</span></p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; color: #666; font-size: 0.85rem;">Current Task</p>
                <p style="margin: 5px 0 0 0; color: #fff; font-weight: 500;">{current_task}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats row
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
            <h3 style="color: #888; font-size: 0.9rem;">CONTACTED</h3>
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
    
    # Activity Log (collapsible)
    with st.expander("📜 Recent Activity", expanded=False):
        activity_log = agent_status.get('activity_log', [])
        if activity_log:
            for entry in activity_log[:10]:
                task_time = entry.get('time', '')
                task_desc = entry.get('task', '')
                if task_time:
                    try:
                        dt = datetime.fromisoformat(task_time.replace('Z', '+00:00'))
                        time_str = dt.strftime("%H:%M")
                    except:
                        time_str = "—"
                else:
                    time_str = "—"
                st.markdown(f"**{time_str}** — {task_desc}")
        else:
            st.markdown("*No recent activity logged*")
    
    st.markdown("---")
    
    # Branch progress
    st.subheader("📈 Branch Progress")
    
    branches = {
        'Mom Influencers (IG)': (30, len([p for p in prospects if p.get('branch') == 'Mom Influencers (IG)'])),
        'Mom Influencers (TT/YT)': (15, len([p for p in prospects if p.get('branch') == 'Mom Influencers (TT/YT)'])),
        'Mom Blogs': (15, len([p for p in prospects if p.get('branch') == 'Mom Blogs'])),
        'Homeschool Influencers (AZ)': (15, len([p for p in prospects if p.get('branch') == 'Homeschool Influencers (AZ)'])),
        'Homeschool Blogs (AZ)': (10, len([p for p in prospects if p.get('branch') == 'Homeschool Blogs (AZ)'])),
        'Homeschool Expansion': (10, len([p for p in prospects if p.get('branch') == 'Homeschool Expansion']))
    }
    
    for branch, (target, current) in branches.items():
        progress = min(current / target * 100, 100) if target > 0 else 0
        color = "#22c55e" if progress >= 100 else "#f59e0b" if progress >= 50 else "#ef4444"
        st.progress(progress / 100, text=f"{branch}: {current}/{target}")
    
    st.markdown("---")
    
    # Action items
    st.subheader("⚡ Action Items")
    
    if pending_drafts > 0:
        st.warning(f"🚨 **{pending_drafts} drafts pending approval** — Go to **Morning Batch** to review and send")
    else:
        st.success("✅ No pending drafts — Scout will continue prospecting")
    
    gap = 95 - total_prospects
    if gap > 0:
        st.info(f"📋 Pipeline gap: {gap} prospects needed to reach 95 target")

# ========== MORNING BATCH VIEW ==========
elif page == "☀️ Morning Batch":
    st.title("☀️ Morning Batch")
    st.markdown("**Approve drafts → Scout sends via AgentMail within 5 minutes**")
    st.markdown("---")
    
    # Get prospects with emails that are pending
    pending = [p for p in prospects 
               if p.get('draft_status') == 'pending' 
               and p.get('email') 
               and '@' in str(p.get('email', ''))
               and p.get('stage') == 'Prospected']
    
    # Sort by score (highest first)
    pending = sorted(pending, key=lambda x: x.get('score', 0), reverse=True)
    
    if not pending:
        st.success("🎉 No pending drafts! All caught up.")
        st.info("Scout will notify you when new prospects are ready for outreach.")
    else:
        st.markdown(f"### 🚨 {len(pending)} drafts waiting for approval")
        
        # Approve All button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("✅ Approve All", type="primary", use_container_width=True):
                for p in pending:
                    p['draft_status'] = 'approved'
                    p['approved_at'] = datetime.now().isoformat()
                save_data(data)
                st.success(f"✅ Approved {len(pending)} drafts! Scout will send within 5 minutes.")
                st.balloons()
                st.rerun()
        
        with col2:
            st.info("Or review individually below")
        
        st.markdown("---")
        
        # Individual approval cards
        for prospect in pending:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="prospect-card pending">
                        <h3 style="margin: 0; color: #fff;">{prospect['name']}</h3>
                        <p style="margin: 5px 0; color: #888;">
                            {prospect['branch']} • {prospect['city']} • Score: <b>{prospect['score']}</b>
                        </p>
                        <p style="margin: 5px 0; color: #666; font-size: 0.85rem;">
                            {prospect.get('handle', '')} • {prospect['email']}
                        </p>
                        <p style="margin: 5px 0; color: #888; font-size: 0.85rem;">
                            <i>"{prospect.get('personalization', '')}"</i>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"✅ Approve", key=f"approve_{prospect['id']}", type="primary", use_container_width=True):
                        prospect['draft_status'] = 'approved'
                        prospect['approved_at'] = datetime.now().isoformat()
                        save_data(data)
                        st.success(f"✅ Approved: {prospect['name']}")
                        st.rerun()
                    
                    if st.button(f"⏭️ Skip", key=f"skip_{prospect['id']}", use_container_width=True):
                        prospect['draft_status'] = 'skipped'
                        save_data(data)
                        st.info(f"⏭️ Skipped: {prospect['name']}")
                        st.rerun()
                
                st.markdown("---")

# ========== PIPELINE VIEW ==========
elif page == "👥 Pipeline":
    st.title("👥 Pipeline")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        branches = sorted(list(set([p.get('branch', 'Unknown') for p in prospects])))
        branch_filter = st.multiselect("Branch", options=branches, default=[])
    
    with col2:
        cities = sorted(list(set([p.get('city', 'Unknown') for p in prospects])))
        city_filter = st.multiselect("City", options=cities, default=[])
    
    with col3:
        stages = ['Prospected', 'Contacted', 'Replied', 'Negotiating', 'Live', 'Cold', 'Skipped']
        stage_filter = st.multiselect("Stage", options=stages, default=[])
    
    # Apply filters
    filtered = prospects
    if branch_filter:
        filtered = [p for p in filtered if p.get('branch') in branch_filter]
    if city_filter:
        filtered = [p for p in filtered if p.get('city') in city_filter]
    if stage_filter:
        filtered = [p for p in filtered if p.get('stage') in stage_filter]
    
    st.markdown(f"**{len(filtered)} prospects** matching filters")
    
    if filtered:
        # Create display data
        display_data = []
        for p in filtered:
            display_data.append({
                'Name': p.get('name', ''),
                'Handle': p.get('handle', ''),
                'City': p.get('city', ''),
                'Branch': p.get('branch', ''),
                'Score': p.get('score', 0),
                'Stage': p.get('stage', ''),
                'Email': p.get('email', '')[:30] + '...' if len(p.get('email', '')) > 30 else p.get('email', '')
            })
        
        st.dataframe(display_data, use_container_width=True, hide_index=True)
    else:
        st.info("No prospects match your filters.")

# ========== INBOX VIEW ==========
elif page == "📥 Inbox":
    st.title("📥 Inbox")
    
    replies = data.get('replies', [])
    
    if not replies:
        st.info("📭 No replies yet. When prospects respond, they'll appear here.")
        st.markdown("""
        **How it works:**
        1. Scout checks AgentMail inbox every 30 minutes
        2. New replies appear here, sorted by urgency  
        3. You provide guidance on how to respond
        4. Scout drafts response → you approve → Scout sends
        """)
    else:
        for reply in replies:
            st.markdown(f"**Reply from {reply.get('from_name', 'Unknown')}**")
            st.info(reply.get('body', 'No content'))

# ========== KNOWLEDGE BASE VIEW ==========
elif page == "🧠 Knowledge Base":
    st.title("🧠 Knowledge Base")
    
    interactions = data.get('interactions', [])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Interactions", len(interactions))
    
    with col2:
        patterns = set(i.get('pattern_tag', '') for i in interactions if i.get('pattern_tag'))
        st.metric("Patterns Identified", len(patterns))
    
    if not interactions:
        st.info("📝 No interactions logged yet. As you process replies, this becomes your playbook.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<p style='text-align: center; color: #666;'>
    Scout v1.0 • Thoven Outreach<br>
    Priority: Approvals → Inbox → Prospecting
</p>
""", unsafe_allow_html=True)

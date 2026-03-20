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
    .main {
        background-color: #0f0f0f;
    }
    .stApp {
        background-color: #0f0f0f;
    }
    .metric-card {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .prospect-card {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .hot-lead {
        border-left: 4px solid #ef4444;
    }
    .pending {
        border-left: 4px solid #f59e0b;
    }
    .approved {
        border-left: 4px solid #22c55e;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
    }
    .approve-btn > button {
        background-color: #22c55e;
        color: white;
    }
    .edit-btn > button {
        background-color: #3b82f6;
        color: white;
    }
    .skip-btn > button {
        background-color: #6b7280;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'prospects' not in st.session_state:
    st.session_state.prospects = pd.DataFrame([
        {
            'id': 1,
            'name': 'Devon Kirby',
            'handle': '@momapprovedmiami',
            'platform': 'Instagram',
            'city': 'Miami',
            'branch': 'Mom Influencers (IG)',
            'followers': '15K-50K',
            'email': 'hello@momapprovedmiami.com',
            'score': 85,
            'stage': 'Prospected',
            'last_contact': None,
            'next_followup': None,
            'notes': 'Miami family activities guide'
        },
        {
            'id': 2,
            'name': 'Christie Ferrari',
            'handle': '@christie_ferrari',
            'platform': 'Instagram',
            'city': 'Miami',
            'branch': 'Mom Influencers (IG)',
            'followers': '100K+',
            'email': 'christieferrari.com/services',
            'score': 90,
            'stage': 'Prospected',
            'last_contact': None,
            'next_followup': None,
            'notes': 'Clinical psychologist, fashion/lifestyle'
        },
        {
            'id': 3,
            'name': 'Jasmine Shefer',
            'handle': '@jasmine_shefer',
            'platform': 'Instagram',
            'city': 'Miami',
            'branch': 'Mom Influencers (IG)',
            'followers': '10K-50K',
            'email': '',
            'score': 75,
            'stage': 'Prospected',
            'last_contact': None,
            'next_followup': None,
            'notes': 'Florida mom, comedy/lifestyle'
        }
    ])

if 'drafts' not in st.session_state:
    st.session_state.drafts = [
        {
            'id': 1,
            'prospect_id': 1,
            'name': 'Devon Kirby',
            'branch': 'Mom Influencers (IG)',
            'city': 'Miami',
            'score': 85,
            'type': 'initial',
            'subject': 'Partnership: Music Education for Miami Families',
            'body': """Hi Devon,

This is Keri! I'm a pianist, music teacher, and co-founder of Thoven — an all-in-one music education platform where families can find verified, background-checked teachers trained at top schools like The Juilliard School.

I love how Mom Approved Miami connects families with the best of South Florida. Your recent post about [specific content] really resonated with me — it shows how much you care about helping parents find quality experiences for their kids.

I'd love to explore a partnership where your audience could get exclusive access to music lessons with our Juilliard-trained teachers. We've seen incredible results with families who never thought music education was accessible to them.

Would you be open to a quick chat about how this might work for your community?

Looking forward to connecting,
Keri Erten
Co-Founder, Thoven
thoven.com""",
            'status': 'pending'
        }
    ]

if 'replies' not in st.session_state:
    st.session_state.replies = []

if 'interactions' not in st.session_state:
    st.session_state.interactions = []

# Sidebar navigation
st.sidebar.title("🎯 Scout Command Center")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "☀️ Morning Batch", "👥 Pipeline", "📥 Inbox", "🧠 Knowledge Base"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")

# Calculate stats
total_prospects = len(st.session_state.prospects)
contacted = len(st.session_state.prospects[st.session_state.prospects['stage'] == 'Contacted'])
replied = len(st.session_state.prospects[st.session_state.prospects['stage'] == 'Replied'])
negotiating = len(st.session_state.prospects[st.session_state.prospects['stage'] == 'Negotiating'])
live = 1  # Audrey Mora

pending_drafts = len([d for d in st.session_state.drafts if d['status'] == 'pending'])
replies_waiting = len(st.session_state.replies)

st.sidebar.metric("Pipeline", f"{total_prospects}/95")
st.sidebar.metric("Pending Drafts", pending_drafts)
st.sidebar.metric("Replies Waiting", replies_waiting)

# ========== DASHBOARD VIEW ==========
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    
    # Metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #888; font-size: 0.9rem;">TOTAL PIPELINE</h3>
            <h1 style="color: #22c55e; font-size: 2.5rem; margin: 10px 0;">{}</h1>
            <p style="color: #666;">of 95 target</p>
        </div>
        """.format(total_prospects), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #888; font-size: 0.9rem;">CONTACTED THIS WEEK</h3>
            <h1 style="color: #3b82f6; font-size: 2.5rem; margin: 10px 0;">{}</h1>
            <p style="color: #666;">outreach sent</p>
        </div>
        """.format(contacted), unsafe_allow_html=True)
    
    with col3:
        reply_rate = f"{(replied/max(contacted,1)*100):.0f}%" if contacted > 0 else "—"
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #888; font-size: 0.9rem;">REPLY RATE</h3>
            <h1 style="color: #f59e0b; font-size: 2.5rem; margin: 10px 0;">{}</h1>
            <p style="color: #666;">{} replies</p>
        </div>
        """.format(reply_rate, replied), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #888; font-size: 0.9rem;">ACTIVE PARTNERS</h3>
            <h1 style="color: #a78bfa; font-size: 2.5rem; margin: 10px 0;">{}</h1>
            <p style="color: #666;">Audrey Mora</p>
        </div>
        """.format(live), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Branch progress
    st.subheader("📈 Branch Progress")
    
    branches = {
        'Mom Influencers (IG)': (30, len(st.session_state.prospects[st.session_state.prospects['branch'] == 'Mom Influencers (IG)'])),
        'Mom Influencers (TT/YT)': (15, 0),
        'Mom Blogs': (15, 0),
        'Homeschool Influencers (AZ)': (15, 0),
        'Homeschool Blogs (AZ)': (10, 0),
        'Homeschool Expansion': (10, 0)
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
        # Calculate overdue follow-ups
        overdue = 0
        for _, prospect in st.session_state.prospects.iterrows():
            if prospect['next_followup'] and pd.notna(prospect['next_followup']):
                if pd.to_datetime(prospect['next_followup']) < datetime.now():
                    overdue += 1
        st.metric("⏰ Follow-ups Overdue", overdue)

# ========== MORNING BATCH VIEW ==========
elif page == "☀️ Morning Batch":
    st.title("☀️ Morning Batch")
    st.markdown("Review and approve today's outreach. This is your main daily workflow.")
    st.markdown("---")
    
    # Pending drafts
    pending = [d for d in st.session_state.drafts if d['status'] == 'pending']
    
    if not pending:
        st.success("🎉 No pending drafts! All caught up.")
        st.info("Scout will queue new prospects here when they're ready for outreach.")
    else:
        # Approve All button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("✅ Approve All", type="primary", use_container_width=True):
                for draft in pending:
                    draft['status'] = 'approved'
                    # Update prospect stage
                    st.session_state.prospects.loc[
                        st.session_state.prospects['id'] == draft['prospect_id'], 
                        'stage'
                    ] = 'Contacted'
                    st.session_state.prospects.loc[
                        st.session_state.prospects['id'] == draft['prospect_id'], 
                        'last_contact'
                    ] = datetime.now()
                st.success(f"Approved {len(pending)} drafts! Ready to send via AgentMail.")
                st.rerun()
        
        with col2:
            st.markdown(f"**{len(pending)} drafts** waiting for approval")
        
        st.markdown("---")
        
        # Draft cards
        for draft in pending:
            with st.container():
                st.markdown(f"""
                <div class="prospect-card pending">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h3 style="margin: 0; color: #fff;">{draft['name']}</h3>
                            <p style="margin: 5px 0; color: #888;">
                                {draft['branch']} • {draft['city']} • Score: <b>{draft['score']}</b>
                            </p>
                        </div>
                        <span style="background: #f59e0b; color: #000; padding: 4px 12px; border-radius: 12px; font-size: 0.8rem;">
                            {draft['type'].upper()}
                        </span>
                    </div>
                    <hr style="border-color: #333; margin: 15px 0;">
                    <p style="color: #888; margin-bottom: 5px;"><b>Subject:</b> {draft['subject']}</p>
                    <div style="background: #252525; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <pre style="white-space: pre-wrap; color: #ccc; font-family: inherit; margin: 0;">{draft['body']}</pre>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"✅ Approve", key=f"approve_{draft['id']}", type="primary", use_container_width=True):
                        draft['status'] = 'approved'
                        st.session_state.prospects.loc[
                            st.session_state.prospects['id'] == draft['prospect_id'], 
                            'stage'
                        ] = 'Contacted'
                        st.session_state.prospects.loc[
                            st.session_state.prospects['id'] == draft['prospect_id'], 
                            'last_contact'
                        ] = datetime.now()
                        st.success(f"Approved: {draft['name']}")
                        st.rerun()
                
                with col2:
                    if st.button(f"✏️ Edit", key=f"edit_{draft['id']}", use_container_width=True):
                        st.session_state[f"editing_{draft['id']}"] = True
                        st.rerun()
                
                with col3:
                    if st.button(f"⏭️ Skip", key=f"skip_{draft['id']}", use_container_width=True):
                        draft['status'] = 'skipped'
                        st.info(f"Skipped: {draft['name']}")
                        st.rerun()
                
                # Edit form
                if st.session_state.get(f"editing_{draft['id']}", False):
                    with st.form(f"edit_form_{draft['id']}"):
                        new_subject = st.text_input("Subject", draft['subject'])
                        new_body = st.text_area("Body", draft['body'], height=200)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                                draft['subject'] = new_subject
                                draft['body'] = new_body
                                st.session_state[f"editing_{draft['id']}"] = False
                                st.success("Changes saved!")
                                st.rerun()
                        with col2:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                st.session_state[f"editing_{draft['id']}"] = False
                                st.rerun()
                
                st.markdown("---")

# ========== PIPELINE VIEW ==========
elif page == "👥 Pipeline":
    st.title("👥 Pipeline")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        branch_filter = st.multiselect(
            "Branch",
            options=st.session_state.prospects['branch'].unique(),
            default=[]
        )
    
    with col2:
        city_filter = st.multiselect(
            "City",
            options=st.session_state.prospects['city'].unique(),
            default=[]
        )
    
    with col3:
        stage_filter = st.multiselect(
            "Stage",
            options=['Prospected', 'Contacted', 'Replied', 'Negotiating', 'Live', 'Cold'],
            default=[]
        )
    
    with col4:
        score_range = st.slider("Score Range", 0, 100, (0, 100))
    
    # Apply filters
    filtered_df = st.session_state.prospects.copy()
    
    if branch_filter:
        filtered_df = filtered_df[filtered_df['branch'].isin(branch_filter)]
    if city_filter:
        filtered_df = filtered_df[filtered_df['city'].isin(city_filter)]
    if stage_filter:
        filtered_df = filtered_df[filtered_df['stage'].isin(stage_filter)]
    filtered_df = filtered_df[
        (filtered_df['score'] >= score_range[0]) & 
        (filtered_df['score'] <= score_range[1])
    ]
    
    st.markdown(f"**{len(filtered_df)} prospects** matching filters")
    
    # Display table
    if len(filtered_df) > 0:
        st.dataframe(
            filtered_df[['name', 'handle', 'city', 'branch', 'score', 'stage', 'email']],
            use_container_width=True,
            hide_index=True
        )
        
        # Prospect detail expander
        st.markdown("---")
        st.subheader("Prospect Details")
        
        selected = st.selectbox(
            "Select a prospect to view details",
            options=filtered_df['name'].tolist()
        )
        
        if selected:
            prospect = filtered_df[filtered_df['name'] == selected].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Name:** {prospect['name']}")
                st.markdown(f"**Handle:** {prospect['handle']}")
                st.markdown(f"**Platform:** {prospect['platform']}")
                st.markdown(f"**City:** {prospect['city']}")
            
            with col2:
                st.markdown(f"**Branch:** {prospect['branch']}")
                st.markdown(f"**Score:** {prospect['score']}")
                st.markdown(f"**Stage:** {prospect['stage']}")
                st.markdown(f"**Email:** {prospect['email']}")
            
            st.markdown(f"**Notes:** {prospect['notes']}")
            
            if pd.notna(prospect['last_contact']):
                st.markdown(f"**Last Contact:** {prospect['last_contact']}")
    else:
        st.info("No prospects match your filters.")

# ========== INBOX VIEW ==========
elif page == "📥 Inbox":
    st.title("📥 Inbox")
    
    if not st.session_state.replies:
        st.info("📭 No replies yet. When prospects respond to your outreach, they'll appear here.")
        st.markdown("""
        **How it works:**
        1. Scout checks AgentMail inbox every 30 minutes
        2. New replies appear here, sorted by urgency
        3. Hot leads flagged in red
        4. You provide guidance, Scout drafts response
        5. You approve, Scout sends
        """)
    else:
        # Sort by urgency (hot leads first)
        sorted_replies = sorted(
            st.session_state.replies, 
            key=lambda x: 0 if x.get('urgency') == 'hot' else 1
        )
        
        for reply in sorted_replies:
            urgency_class = "hot-lead" if reply.get('urgency') == 'hot' else ""
            
            st.markdown(f"""
            <div class="prospect-card {urgency_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0;">🔔 {reply['from_name']}</h3>
                    <span style="color: #888;">{reply['timestamp']}</span>
                </div>
                <p style="color: #888;">{reply['from_email']} • {reply.get('branch', 'Unknown branch')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Their reply:**")
                st.info(reply['body'])
            
            with col2:
                st.markdown("**Our original outreach:**")
                st.text(reply.get('original_outreach', 'N/A'))
            
            # Guidance input
            st.markdown("**Your guidance:**")
            guidance = st.text_area(
                "Tell Scout how to respond",
                key=f"guidance_{reply['id']}",
                placeholder="e.g., 'Thank them and offer a 15-min call next Tuesday'"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📝 Generate Draft", key=f"gen_{reply['id']}", use_container_width=True):
                    # In real implementation, this would call the AI
                    st.session_state[f"draft_{reply['id']}"] = f"Draft based on: {guidance}"
                    st.rerun()
            
            with col2:
                if st.button("✉️ Quick Reply", key=f"quick_{reply['id']}", use_container_width=True):
                    st.info("Quick reply templates coming in V2")
            
            st.markdown("---")

# ========== KNOWLEDGE BASE VIEW ==========
elif page == "🧠 Knowledge Base":
    st.title("🧠 Knowledge Base")
    
    # Stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Interactions", len(st.session_state.interactions))
    
    with col2:
        patterns = set(i.get('pattern_tag', '') for i in st.session_state.interactions)
        st.metric("Patterns Identified", len(patterns))
    
    with col3:
        st.metric("Response Templates", 0)
    
    st.markdown("---")
    
    if not st.session_state.interactions:
        st.info("📝 No interactions logged yet. As you process replies, this becomes your playbook.")
        st.markdown("""
        **What gets logged:**
        - Every prospect reply and your response
        - What worked and what didn't
        - Pattern tags (e.g., "pricing question", "scheduling request")
        - Outcomes (converted, cold, negotiating)
        
        **Why it matters:**
        After 1-2 weeks, Scout will recognize patterns and suggest responses based on similar past situations.
        """)
    else:
        # Search/filter
        search = st.text_input("Search interactions")
        pattern_filter = st.multiselect(
            "Filter by pattern",
            options=list(set(i.get('pattern_tag', '') for i in st.session_state.interactions))
        )
        
        # Display interactions
        for interaction in st.session_state.interactions:
            with st.expander(f"{interaction['prospect_name']} — {interaction['pattern_tag']}"):
                st.markdown(f"**Situation:** {interaction['situation']}")
                st.markdown(f"**Guidance:** {interaction['guidance']}")
                st.markdown(f"**Response sent:** {interaction['response']}")
                st.markdown(f"**Outcome:** {interaction['outcome']}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("<p style='text-align: center; color: #666;'>Scout v1.0 • Thoven Outreach</p>", unsafe_allow_html=True)

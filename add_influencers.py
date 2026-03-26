import json
from datetime import datetime

# Load existing data
with open('scout_data.json', 'r') as f:
    data = json.load(f)

# New TikTok/YouTube influencers
new_influencers = [
    {
        "id": "tt_miami_001",
        "name": "Myriam Sandler",
        "handle": "@mothercould",
        "platform": "TikTok/Instagram",
        "city": "Miami",
        "branch": "Mom Influencers (TT/YT)",
        "followers": "1.6M IG / 721K TikTok",
        "email": "",
        "score": 92,
        "stage": "Prospected",
        "notes": "DIY kids activities, sensory play, Mothercould brand",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "tt_la_001",
        "name": "Angela Rose",
        "handle": "@angelarosehome",
        "platform": "TikTok/Instagram",
        "city": "LA",
        "branch": "Mom Influencers (TT/YT)",
        "followers": "1.4M IG / 695K TikTok",
        "email": "",
        "score": 90,
        "stage": "Prospected",
        "notes": "DIY home decor, Fearless DIY motto, mom of 3",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "tt_chi_001",
        "name": "Casey Finn",
        "handle": "@diyplaybook",
        "platform": "TikTok/Instagram",
        "city": "Chicago",
        "branch": "Mom Influencers (TT/YT)",
        "followers": "854K IG / 161K TikTok",
        "email": "",
        "score": 88,
        "stage": "Prospected",
        "notes": "DIY Playbook, home DIY, Chicago mom",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "yt_la_001",
        "name": "Brittany Vasseur",
        "handle": "@vasseurbeauty",
        "platform": "YouTube/Instagram",
        "city": "LA",
        "branch": "Mom Influencers (TT/YT)",
        "followers": "1.5M YT / 197K IG",
        "email": "",
        "score": 89,
        "stage": "Prospected",
        "notes": "Life hacks, home organization, cleaning, mom of 2",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "tt_miami_002",
        "name": "Lele Pons",
        "handle": "@lelepons",
        "platform": "TikTok/YouTube",
        "city": "Miami",
        "branch": "Mom Influencers (TT/YT)",
        "followers": "50M+",
        "email": "",
        "score": 95,
        "stage": "Prospected",
        "notes": "Venezuelan-American creator, comedy, music, moved to Miami",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "tt_miami_003",
        "name": "Michelle Lewin",
        "handle": "@michelle_lewin",
        "platform": "TikTok/Instagram",
        "city": "Miami",
        "branch": "Mom Influencers (TT/YT)",
        "followers": "15M",
        "email": "",
        "score": 88,
        "stage": "Prospected",
        "notes": "Fitness icon, workout routines, Miami-based Venezuelan",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "tt_la_002",
        "name": "Melissa Christine",
        "handle": "@melissacgeraghty",
        "platform": "TikTok",
        "city": "LA",
        "branch": "Mom Influencers (TT/YT)",
        "followers": "35K TikTok",
        "email": "",
        "score": 76,
        "stage": "Prospected",
        "notes": "LA mom, beauty, girly content",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "tt_la_003",
        "name": "Cristina Ochoa",
        "handle": "@vivacristina",
        "platform": "TikTok",
        "city": "LA",
        "branch": "Mom Influencers (TT/YT)",
        "followers": "19.6K TikTok",
        "email": "",
        "score": 74,
        "stage": "Prospected",
        "notes": "Latina mom, LA-based",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    }
]

# Arizona homeschool organizations/blogs
new_homeschool = [
    {
        "id": "az_hs_org_001",
        "name": "Arizona Families for Home Education",
        "handle": "@afheorg",
        "platform": "Website/Org",
        "city": "Phoenix",
        "branch": "Homeschool Blogs (AZ)",
        "followers": "",
        "email": "homeschool@afhe.org",
        "score": 90,
        "stage": "Prospected",
        "notes": "Statewide homeschool organization since 1983, 501(c)(3), annual convention",
        "personalization": "AFHE has been serving Arizona homeschool families for over 40 years with incredible dedication",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "az_hs_org_002",
        "name": "We Make History",
        "handle": "",
        "platform": "Website/Org",
        "city": "Phoenix",
        "branch": "Homeschool Blogs (AZ)",
        "followers": "",
        "email": "wemakehistory@aol.com",
        "score": 85,
        "stage": "Prospected",
        "notes": "Educational enterprise, historic balls, arts events, serves thousands of homeschoolers",
        "personalization": "your events bring history and arts to life for thousands of Arizona homeschool families",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "az_hs_org_003",
        "name": "Covenant Home School Resource Center",
        "handle": "@chsrc",
        "platform": "Website/Org",
        "city": "Phoenix",
        "branch": "Homeschool Blogs (AZ)",
        "followers": "",
        "email": "info@chsrc.org",
        "score": 84,
        "stage": "Prospected",
        "notes": "Only homeschool bookstore in Arizona, support services",
        "personalization": "as the only homeschool bookstore in Arizona, you're a crucial hub for the community",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "az_hs_org_004",
        "name": "Quest for Education and Arts",
        "handle": "",
        "platform": "Website/Org",
        "city": "Tucson",
        "branch": "Homeschool Blogs (AZ)",
        "followers": "",
        "email": "office@questforeducationandarts.com",
        "score": 82,
        "stage": "Prospected",
        "notes": "501c3 non-profit, STEAM instruction, Christ-centered, Southern Arizona",
        "personalization": "your hands-on STEAM approach in a Christ-centered environment fills such a needed gap",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "az_hs_org_005",
        "name": "Sonoran Desert Homeschoolers",
        "handle": "",
        "platform": "Website/Facebook",
        "city": "Tucson",
        "branch": "Homeschool Blogs (AZ)",
        "followers": "",
        "email": "",
        "score": 78,
        "stage": "Prospected",
        "notes": "Tucson homeschool support group, community events",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "az_hs_org_006",
        "name": "HEArts AZ",
        "handle": "",
        "platform": "Facebook",
        "city": "Phoenix",
        "branch": "Homeschool Blogs (AZ)",
        "followers": "",
        "email": "",
        "score": 76,
        "stage": "Prospected",
        "notes": "Home Education & Arts in Arizona, Maricopa County, creative focus",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    }
]

# Combine all new prospects
all_new = new_influencers + new_homeschool

# Check for duplicates and add
existing_ids = {p['id'] for p in data['prospects']}
added = 0

for prospect in all_new:
    if prospect['id'] not in existing_ids:
        data['prospects'].append(prospect)
        added += 1
        print(f"✅ Added: {prospect['name']} ({prospect['branch']})")
    else:
        print(f"⏭️  Skipped: {prospect['name']}")

# Update stats
data['stats']['total_prospects'] = len(data['prospects'])

# Save
with open('scout_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n📊 Added {added} new prospects")
print(f"📊 Total prospects: {data['stats']['total_prospects']}")
print(f"\n📊 Branch counts:")
for branch in ['Mom Influencers (IG)', 'Mom Influencers (TT/YT)', 'Mom Blogs', 
               'Homeschool Influencers (AZ)', 'Homeschool Blogs (AZ)', 'Homeschool Expansion']:
    count = len([p for p in data['prospects'] if p['branch'] == branch])
    print(f"   {branch}: {count}")

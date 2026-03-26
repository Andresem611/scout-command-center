import json
from datetime import datetime

# Load existing data
with open('scout_data.json', 'r') as f:
    data = json.load(f)

# New mom blogs from research
new_blogs = [
    {
        "id": "la_blog_001",
        "name": "Sarah Auerswald",
        "handle": "@momsla",
        "platform": "Blog",
        "city": "LA",
        "branch": "Mom Blogs",
        "followers": "11.2K IG",
        "email": "Sarah@MomsLA.com",
        "score": 88,
        "stage": "Prospected",
        "notes": "MomsLA founder, LA family activities",
        "personalization": "MomsLA has been the go-to resource for LA families since 2011",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "la_blog_002",
        "name": "Tracy Fredkin",
        "handle": "",
        "platform": "Blog",
        "city": "LA",
        "branch": "Mom Blogs",
        "followers": "",
        "email": "Tracy@FunFamilyBrands.com",
        "score": 85,
        "stage": "Prospected",
        "notes": "SoCalMoms founder, partners with MomsLA",
        "personalization": "your work with SoCalMoms and Fun Family Brands connects so many families",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "la_blog_003",
        "name": "Tirralan",
        "handle": "@tinseltownmom",
        "platform": "Blog",
        "city": "LA",
        "branch": "Mom Blogs",
        "followers": "10K",
        "email": "",
        "score": 78,
        "stage": "Prospected",
        "notes": "Tinseltown Mom, famous mothers focus",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "la_blog_004",
        "name": "Jenna Greenspoon",
        "handle": "@savvysassymoms",
        "platform": "Blog",
        "city": "LA",
        "branch": "Mom Blogs",
        "followers": "64.2K IG",
        "email": "",
        "score": 86,
        "stage": "Prospected",
        "notes": "Savvy Sassy Moms, parenting tips",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "la_blog_005",
        "name": "Anabel Marquez",
        "handle": "@dotellanabel",
        "platform": "Blog",
        "city": "LA",
        "branch": "Mom Blogs",
        "followers": "",
        "email": "DoTellAnabel@gmail.com",
        "score": 84,
        "stage": "Prospected",
        "notes": "Do Tell Anabel blog, Long Beach/SoCal focus",
        "personalization": "your perspective as a Long Beach mom brings such authentic SoCal flavor",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "chi_blog_001",
        "name": "Karen Alpert",
        "handle": "@babysideburns",
        "platform": "Blog",
        "city": "Chicago",
        "branch": "Mom Blogs",
        "followers": "",
        "email": "",
        "score": 87,
        "stage": "Prospected",
        "notes": "Baby Sideburns, NYT bestseller, hilarious parenting",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "chi_blog_002",
        "name": "Ceta Walters",
        "handle": "@clarkandstone",
        "platform": "Blog",
        "city": "Chicago",
        "branch": "Mom Blogs",
        "followers": "",
        "email": "",
        "score": 85,
        "stage": "Prospected",
        "notes": "Clark and Stone, style/travel/breast cancer survivor",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "chi_blog_003",
        "name": "Helen Berkun",
        "handle": "@helen_berkun",
        "platform": "Blog",
        "city": "Chicago",
        "branch": "Mom Blogs",
        "followers": "",
        "email": "",
        "score": 82,
        "stage": "Prospected",
        "notes": "Chicago lifestyle, style, home, travel",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "hou_blog_001",
        "name": "Stacey Rodriguez",
        "handle": "@thesoccermomblog",
        "platform": "Blog",
        "city": "Houston",
        "branch": "Mom Blogs",
        "followers": "",
        "email": "StaceyGarska@gmail.com",
        "score": 86,
        "stage": "Prospected",
        "notes": "The Soccer Mom Blog, Houston parenting, 3 girls",
        "personalization": "your Houston family content and soccer mom perspective is so relatable",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "hou_blog_002",
        "name": "Second City Mom",
        "handle": "@secondcitymom",
        "platform": "Blog",
        "city": "Houston",
        "branch": "Mom Blogs",
        "followers": "",
        "email": "contact@secondcitymom.com",
        "score": 80,
        "stage": "Prospected",
        "notes": "Houston mom blog",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "dallas_blog_001",
        "name": "Heather Buen",
        "handle": "@dallassinglemom",
        "platform": "Blog",
        "city": "Dallas",
        "branch": "Mom Blogs",
        "followers": "3.9K IG",
        "email": "",
        "score": 81,
        "stage": "Prospected",
        "notes": "Dallas Single Mom, MBA, life transitions",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    }
]

# Check for duplicates and add new ones
existing_ids = {p['id'] for p in data['prospects']}
added = 0

for blog in new_blogs:
    if blog['id'] not in existing_ids:
        data['prospects'].append(blog)
        added += 1
        print(f"✅ Added: {blog['name']} ({blog['city']})")
    else:
        print(f"⏭️  Skipped (duplicate): {blog['name']}")

# Update stats
data['stats']['total_prospects'] = len(data['prospects'])

# Save
with open('scout_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n📊 Added {added} new blogs")
print(f"📊 Total prospects: {data['stats']['total_prospects']}")
print(f"📊 Branch counts:")
for branch in ['Mom Influencers (IG)', 'Mom Influencers (TT/YT)', 'Mom Blogs', 
               'Homeschool Influencers (AZ)', 'Homeschool Blogs (AZ)', 'Homeschool Expansion']:
    count = len([p for p in data['prospects'] if p['branch'] == branch])
    print(f"   {branch}: {count}")

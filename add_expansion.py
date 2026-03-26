import json
from datetime import datetime

# Load existing data
with open('scout_data.json', 'r') as f:
    data = json.load(f)

# Homeschool expansion prospects (FL, TX, UT)
new_expansion = [
    {
        "id": "fl_hs_001",
        "name": "Florida Parent Educators Association",
        "handle": "@fpeaflorida",
        "platform": "Website/Org",
        "city": "Orlando",
        "branch": "Homeschool Expansion",
        "followers": "",
        "email": "",
        "score": 92,
        "stage": "Prospected",
        "notes": "Largest statewide homeschool org in FL, annual convention Orlando, thousands of families",
        "personalization": "FPEA represents thousands of Florida homeschool families and your annual convention is legendary",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "fl_hs_002",
        "name": "The Homeschool Hive",
        "handle": "@thehomeschoolhive",
        "platform": "Website/Store",
        "city": "Tampa",
        "branch": "Homeschool Expansion",
        "followers": "",
        "email": "",
        "score": 86,
        "stage": "Prospected",
        "notes": "Florida's only homeschool store, portfolio evaluations, family-run",
        "personalization": "as Florida's only homeschool store, you're at the center of the community",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "fl_hs_003",
        "name": "Tampa Bay Homeschool MUN",
        "handle": "@tbhmun",
        "platform": "Website/Org",
        "city": "Tampa",
        "branch": "Homeschool Expansion",
        "followers": "",
        "email": "contact@tbhmun.com",
        "score": 82,
        "stage": "Prospected",
        "notes": "Model UN for homeschoolers, competitive teams, high school and middle school",
        "personalization": "your Model UN program gives homeschoolers incredible leadership opportunities",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "tx_hs_001",
        "name": "Texas Home School Coalition",
        "handle": "@thsc",
        "platform": "Website/Org",
        "city": "Dallas/Fort Worth",
        "branch": "Homeschool Expansion",
        "followers": "58K+ Facebook",
        "email": "sales@thsc.org",
        "score": 94,
        "stage": "Prospected",
        "notes": "Major statewide org, 72K+ newsletter subscribers, 2 conventions/year, Capitol Days",
        "personalization": "THSC's reach across Texas with 72,000 newsletter subscribers is remarkable",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "tx_hs_002",
        "name": "Texas Homeschool Alliance",
        "handle": "",
        "platform": "Website/Org",
        "city": "Austin",
        "branch": "Homeschool Expansion",
        "followers": "",
        "email": "registrar@texashomeschoolalliance.com",
        "score": 84,
        "stage": "Prospected",
        "notes": "Austin-based homeschool support, classes and programs",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "tx_hs_003",
        "name": "Forge Christian Homeschool Community",
        "handle": "",
        "platform": "Co-op",
        "city": "Austin",
        "branch": "Homeschool Expansion",
        "followers": "",
        "email": "",
        "score": 80,
        "stage": "Prospected",
        "notes": "Christian homeschool co-op, meets Fridays, Austin area",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "tx_hs_004",
        "name": "Holy Family Homeschoolers",
        "handle": "",
        "platform": "Co-op",
        "city": "Austin",
        "branch": "Homeschool Expansion",
        "followers": "",
        "email": "hfh@groups.io",
        "score": 78,
        "stage": "Prospected",
        "notes": "Catholic homeschoolers, Greater Austin area",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    },
    {
        "id": "tx_hs_005",
        "name": "Frisco Home is School",
        "handle": "@friscohis",
        "platform": "Co-op",
        "city": "Dallas",
        "branch": "Homeschool Expansion",
        "followers": "",
        "email": "",
        "score": 82,
        "stage": "Prospected",
        "notes": "Frisco HIS, large homeschool co-op, Collin/Denton counties",
        "personalization": "",
        "draft_status": "pending",
        "last_contact": None,
        "next_followup": None
    }
]

# Check for duplicates and add
existing_ids = {p['id'] for p in data['prospects']}
added = 0

for prospect in new_expansion:
    if prospect['id'] not in existing_ids:
        data['prospects'].append(prospect)
        added += 1
        print(f"✅ Added: {prospect['name']} ({prospect['city']})")
    else:
        print(f"⏭️  Skipped: {prospect['name']}")

# Update stats
data['stats']['total_prospects'] = len(data['prospects'])

# Save
with open('scout_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n📊 Added {added} new expansion prospects")
print(f"📊 Total prospects: {data['stats']['total_prospects']}")
print(f"\n📊 Final Branch counts:")
for branch in ['Mom Influencers (IG)', 'Mom Influencers (TT/YT)', 'Mom Blogs', 
               'Homeschool Influencers (AZ)', 'Homeschool Blogs (AZ)', 'Homeschool Expansion']:
    count = len([p for p in data['prospects'] if p['branch'] == branch])
    target = {'Mom Influencers (IG)': 30, 'Mom Influencers (TT/YT)': 15, 'Mom Blogs': 15,
              'Homeschool Influencers (AZ)': 15, 'Homeschool Blogs (AZ)': 10, 'Homeschool Expansion': 10}.get(branch, 0)
    status = "✅" if count >= target else "🟡" if count >= target * 0.5 else "🔴"
    print(f"   {status} {branch}: {count}/{target}")

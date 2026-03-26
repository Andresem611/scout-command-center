#!/usr/bin/env python3
"""Sync pipeline markdown files to scout_data.json"""
import json
import re
from datetime import datetime

# Read the geo pipeline file
with open('pipeline/PROSPECTS_GEO_2026-03-26.md', 'r') as f:
    content = f.read()

# Parse prospects from the markdown tables
prospects = []

# Extract influencer tables for each city
# Pattern: | Name | Handle | Followers | Type | Email | Status |
city_pattern = r'##\s+([🏙🌴🤠🌵][^\n]+)\s*\(\d+[^)]*\)[^|]*\n\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|[^\n]+\n\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|([^#]+?)(?=\n##|\n---|$)'

cities = {
    '🏙️ NEW YORK CITY': 'NYC',
    '🌴 MIAMI/SOUTH FLORIDA': 'Miami',
    '🌴 LOS ANGELES': 'LA',
    '🌉 SAN FRANCISCO/BAY AREA': 'SF',
    '🤠 HOUSTON': 'Houston',
    '🤠 DALLAS': 'Dallas',
    '🤠 AUSTIN': 'Austin',
    '🏙️ CHICAGO': 'Chicago',
    '🌵 ARIZONA HOMESCHOOL': 'Arizona'
}

# Parse simple table rows
table_pattern = r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|'

# Manually extract from known sections
sections = content.split('## ')

for section in sections:
    lines = section.split('\n')
    city = None
    
    for city_key, city_short in cities.items():
        if city_key.strip() in section[:100]:
            city = city_short
            break
    
    if not city:
        continue
    
    for line in lines[2:]:  # Skip header and separator
        match = re.match(r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|', line)
        if match:
            name, handle, followers, loc, email, status = [m.strip() for m in match.groups()]
            if name and name != 'Name':
                # Clean up followers
                followers_clean = followers.replace('K', '000').replace('M', '000000').replace('.', '').replace(',', '')
                try:
                    followers_num = int(re.sub(r'[^\d]', '', followers_clean) or '0')
                except:
                    followers_num = 0
                
                # Determine type
                follower_type = 'Nano'
                if followers_num >= 1000000:
                    follower_type = 'Mega'
                elif followers_num >= 500000:
                    follower_type = 'Macro'
                elif followers_num >= 50000:
                    follower_type = 'Micro'
                elif followers_num >= 10000:
                    follower_type = 'Nano'
                
                # Clean email
                email_clean = email if '@' in email else ''
                
                prospects.append({
                    'name': name,
                    'handle': handle.replace('@', ''),
                    'followers': followers_num,
                    'city': city,
                    'email': email_clean,
                    'stage': 'Uncontacted' if 'Uncontacted' in status else status,
                    'type': follower_type,
                    'branch': 'Mom Influencers (IG)' if city != 'Arizona' else 'Homeschool Influencers (AZ)',
                    'score': 5 if email_clean else 3
                })

print(f"Parsed {len(prospects)} prospects from pipeline")

# Load existing data
with open('scout_data.json', 'r') as f:
    data = json.load(f)

# Update prospects
data['prospects'] = prospects

# Update stats
data['stats'] = {
    'total_prospects': len(prospects),
    'contacted': len([p for p in prospects if p.get('stage') == 'Contacted']),
    'replied': len([p for p in prospects if p.get('stage') in ['Replied', 'Negotiating']])
}

# Save
with open('scout_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Updated scout_data.json with {len(prospects)} prospects")
print(f"Stats: {data['stats']}")

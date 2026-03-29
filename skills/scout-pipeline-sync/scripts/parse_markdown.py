#!/usr/bin/env python3
"""
Parse markdown prospect files and extract structured data.
"""

import re
import glob
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class Prospect:
    name: str
    handle: str
    followers: Optional[int]
    email: str
    status: str
    city: str
    branch: str
    source_file: str


def parse_followers(followers_str: str) -> Optional[int]:
    """
    Parse follower counts like '1.6M', '45K', '2K+', '<1K', 'N/A'.
    """
    if not followers_str or followers_str.upper() in ('N/A', 'NA', '-', ''):
        return None
    
    # Clean the string
    s = followers_str.strip().upper()
    
    # Handle <1K case - estimate as 500
    if s.startswith('<'):
        return 500
    
    # Remove + suffix
    s = s.rstrip('+')
    
    # Extract multiplier
    multiplier = 1
    if s.endswith('M'):
        multiplier = 1000000
        s = s[:-1]
    elif s.endswith('K'):
        multiplier = 1000
        s = s[:-1]
    
    # Remove commas and convert
    try:
        s = s.replace(',', '')
        value = float(s)
        return int(value * multiplier)
    except (ValueError, TypeError):
        return None


def map_status(status_str: str) -> str:
    """
    Map markdown status to pipeline stage.
    """
    status_map = {
        'Uncontacted': 'Prospected',
        '✅ LIVE PARTNER': 'Partner',
        'Contacted': 'Contacted',
        'Replied': 'Replied',
        'Negotiating': 'Negotiating',
        'Declined': 'Declined',
    }
    return status_map.get(status_str.strip(), 'Prospected')


def extract_city_from_header(header: str) -> str:
    """
    Extract city name from section header like '### NYC Prospects (18)'.
    """
    # Remove markdown headers
    header = header.lstrip('#').strip()
    
    # Remove parenthetical counts
    header = re.sub(r'\s*\(\d+\)\s*$', '', header)
    
    # Remove common suffixes
    suffixes = ['Prospects', 'Blogs', 'Influencers', 'Influencer']
    for suffix in suffixes:
        if header.endswith(suffix):
            header = header[:-len(suffix)].strip()
    
    return header


def determine_branch(city: str, section_context: str) -> str:
    """
    Determine branch category based on city and context.
    """
    section_lower = section_context.lower()
    
    if 'homeschool' in section_lower:
        return 'Homeschool'
    elif 'blog' in section_lower:
        return 'Mom Blog'
    else:
        return 'Mom Influencers'


def parse_markdown_table(table_lines: List[str], default_city: str, branch: str, source_file: str) -> List[Prospect]:
    """
    Parse a markdown table into Prospect objects.
    Handles multiple table formats.
    """
    prospects = []
    table_format = "standard"  # standard, blog, or extended
    
    for line in table_lines:
        line = line.strip()
        if not line or line.startswith('|---'):
            continue
        
        # Detect table format from header
        if 'Blog Name' in line:
            table_format = "blog"
            continue
        elif '| Name |' in line and 'Location' in line:
            table_format = "extended"
            continue
        elif line.startswith('| Name ') and 'Handle' in line:
            table_format = "standard"
            continue
        
        # Skip header row (already detected above)
        if line.startswith('|:---'):
            continue
        
        # Parse table row
        if line.startswith('|'):
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            
            if table_format == "blog" and len(cells) >= 5:
                # Blog format: Blog Name | City | URL | Contact | Status
                name = cells[0]
                city = cells[1] if cells[1] else default_city
                url = cells[2]  # Could be used as handle
                email = cells[3]
                status = cells[4]
                handle = url if url else name.lower().replace(' ', '_')
                followers = None  # Blogs don't have follower counts
                
                prospect = Prospect(
                    name=name,
                    handle=f"@{handle}",
                    followers=followers,
                    email=email,
                    status=map_status(status),
                    city=city,
                    branch=branch,
                    source_file=source_file
                )
                prospects.append(prospect)
                
            elif table_format == "extended" and len(cells) >= 6:
                # Extended format: Name | Handle | Followers | Location | Email | Status
                name = cells[0]
                handle = cells[1]
                followers_str = cells[2]
                # location = cells[3]  # Not used currently
                email = cells[4]
                status = cells[5]
                
                prospect = Prospect(
                    name=name,
                    handle=handle,
                    followers=parse_followers(followers_str),
                    email=email,
                    status=map_status(status),
                    city=default_city,
                    branch=branch,
                    source_file=source_file
                )
                prospects.append(prospect)
                
            elif len(cells) >= 5:
                # Standard format: Name | Handle | Followers | Email | Status
                name = cells[0]
                handle = cells[1]
                followers_str = cells[2]
                email = cells[3]
                status = cells[4]
                
                prospect = Prospect(
                    name=name,
                    handle=handle,
                    followers=parse_followers(followers_str),
                    email=email,
                    status=map_status(status),
                    city=default_city,
                    branch=branch,
                    source_file=source_file
                )
                prospects.append(prospect)
    
    return prospects


def parse_markdown_file(filepath: str) -> List[Prospect]:
    """
    Parse a single markdown file and return all prospects.
    """
    prospects = []
    current_city = "Unknown"
    current_section = "Mom Influencers"
    source_file = os.path.basename(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Try to extract city from filename
    city_from_filename = None
    filename_lower = source_file.lower()
    if 'nyc' in filename_lower or 'new_york' in filename_lower:
        city_from_filename = "NYC"
    elif 'miami' in filename_lower:
        city_from_filename = "Miami"
    elif 'la' in filename_lower:
        city_from_filename = "LA"
    elif 'sf' in filename_lower or 'bay' in filename_lower:
        city_from_filename = "SF/Bay Area"
    elif 'houston' in filename_lower:
        city_from_filename = "Houston"
    elif 'dallas' in filename_lower:
        city_from_filename = "Dallas"
    elif 'austin' in filename_lower:
        city_from_filename = "Austin"
    elif 'chicago' in filename_lower:
        city_from_filename = "Chicago"
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Detect section headers
        if line.startswith('### '):
            current_city = extract_city_from_header(line)
        elif line.startswith('## '):
            current_section = line.lstrip('#').strip()
            # Reset city for new major section
            if city_from_filename:
                current_city = city_from_filename
        
        # Detect table start (various header formats)
        is_table_start = False
        if '| Blog Name |' in line and 'City' in line:
            is_table_start = True
        elif '| Name |' in line and 'Handle' in line:
            is_table_start = True
        
        if is_table_start:
            # Collect table lines until empty line or non-table line
            table_lines = [line]
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if not next_line or (not next_line.startswith('|') and not next_line.startswith('|---')):
                    break
                table_lines.append(next_line)
                j += 1
            
            branch = determine_branch(current_city, current_section)
            table_prospects = parse_markdown_table(table_lines, current_city, branch, source_file)
            prospects.extend(table_prospects)
            
            i = j - 1
        
        i += 1
    
    return prospects


def parse_all_markdown_files(pipeline_dir: str = None) -> List[Prospect]:
    """
    Parse all PROSPECTS_*.md files in the pipeline directory.
    """
    if pipeline_dir is None:
        # We're in skills/scout-pipeline-sync/scripts/, workspace is 3 levels up
        script_dir = os.path.dirname(os.path.abspath(__file__))
        workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
        pipeline_dir = os.path.join(workspace_root, 'pipeline')
    
    prospects = []
    pattern = os.path.join(pipeline_dir, 'PROSPECTS_*.md')
    
    for filepath in glob.glob(pattern):
        file_prospects = parse_markdown_file(filepath)
        prospects.extend(file_prospects)
        print(f"Parsed {len(file_prospects)} prospects from {os.path.basename(filepath)}")
    
    return prospects


def prospects_to_dicts(prospects: List[Prospect]) -> List[Dict[str, Any]]:
    """
    Convert Prospect objects to dictionaries.
    """
    return [asdict(p) for p in prospects]


if __name__ == '__main__':
    prospects = parse_all_markdown_files()
    print(f"\nTotal prospects parsed: {len(prospects)}")
    
    # Show sample
    if prospects:
        print("\nSample prospect:")
        print(prospects[0])

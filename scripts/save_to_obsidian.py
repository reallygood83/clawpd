"""
Save ClawPD outputs to Obsidian vault
"""
import os
import re
import subprocess
from datetime import datetime

def save_plan_to_obsidian(plan_content, topic, vault_path, plan_folder="500-YouTube/기획안"):
    """Save PD plan as Obsidian note and return file path"""
    if not vault_path:
        return None
    
    folder = os.path.join(vault_path, plan_folder)
    os.makedirs(folder, exist_ok=True)
    
    # Clean filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    clean_topic = re.sub(r'[^\w가-힣\s-]', '', topic)[:40].strip()
    filename = f"기획안-{date_str}-{clean_topic}.md"
    filepath = os.path.join(folder, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(plan_content)
    
    return filepath

def save_swot_to_obsidian(swot_content, vault_path, swot_folder="500-YouTube/SWOT분석"):
    """Save SWOT report as Obsidian note"""
    if not vault_path:
        return None
    
    folder = os.path.join(vault_path, swot_folder)
    os.makedirs(folder, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"SWOT-{date_str}.md"
    filepath = os.path.join(folder, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(swot_content)
    
    return filepath

def try_share_note(vault_name, filepath):
    """Try to generate Share Note link via Advanced URI (optional)"""
    try:
        relative = filepath.split(vault_name + "/")[-1] if vault_name in filepath else filepath
        encoded = relative.replace("/", "%2F").replace(" ", "%20")
        
        # Open in Obsidian
        subprocess.run(["open", f"obsidian://advanced-uri?vault={vault_name}&filepath={encoded}"], check=False)
        import time; time.sleep(3)
        
        # Trigger share
        subprocess.run(["open", f"obsidian://advanced-uri?vault={vault_name}&commandid=share-note%3Ashare-note"], check=False)
        import time; time.sleep(10)
        
        # Read share_link from frontmatter
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        match = re.search(r'share_link:\s*(https?://\S+)', content)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None

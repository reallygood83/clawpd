"""
ClawPD Configuration Manager
Handles user settings including Obsidian vault path
"""
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "config.json")

DEFAULT_CONFIG = {
    "obsidian_vault": "",
    "obsidian_plan_folder": "500-YouTube/기획안",
    "obsidian_swot_folder": "500-YouTube/SWOT분석",
    "auto_save_obsidian": True,
    "share_note_enabled": False,
    "language": "ko",
    "default_video_length": 15,
    "telegram_notify": True
}

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            saved = json.load(f)
            config = DEFAULT_CONFIG.copy()
            config.update(saved)
            return config
    return DEFAULT_CONFIG.copy()

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def get_obsidian_plan_path(config=None):
    if config is None:
        config = load_config()
    vault = config.get("obsidian_vault", "")
    folder = config.get("obsidian_plan_folder", "500-YouTube/기획안")
    if vault:
        path = os.path.join(vault, folder)
        os.makedirs(path, exist_ok=True)
        return path
    return None

def get_obsidian_swot_path(config=None):
    if config is None:
        config = load_config()
    vault = config.get("obsidian_vault", "")
    folder = config.get("obsidian_swot_folder", "500-YouTube/SWOT분석")
    if vault:
        path = os.path.join(vault, folder)
        os.makedirs(path, exist_ok=True)
        return path
    return None

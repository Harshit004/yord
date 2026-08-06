"""
Antigravity-Style Dynamic Skill Search & Auto-Installer for YORD.
Searches local repositories and GitHub / online sources for skills when requested.
Automatically installs SKILL.md packages into /skills/ without requiring server restarts.
RAM Impact: Negligible (<5MB).
"""

import os
import json
import re
import urllib.request
from typing import Dict, Any, Optional

SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../skills"))
GLOBAL_SKILLS_ROOT = os.path.expanduser("~/.agents/skills")

class DynamicSkillInstaller:
    """
    Manages skill discovery, GitHub/web searching, and auto-installation.
    """
    def __init__(self, skills_dir: str = SKILLS_DIR):
        self.skills_dir = skills_dir
        os.makedirs(self.skills_dir, exist_ok=True)

    def is_skill_installed(self, skill_name: str) -> bool:
        target = os.path.join(self.skills_dir, skill_name.lower().replace(" ", "-"))
        return os.path.exists(target) and os.path.exists(os.path.join(target, "SKILL.md"))

    def search_local_global_skills(self, clean_name: str) -> Optional[str]:
        """
        Searches system global skills directory (~/.agents/skills) for pre-existing skills.
        """
        if os.path.exists(GLOBAL_SKILLS_ROOT):
            target = os.path.join(GLOBAL_SKILLS_ROOT, clean_name, "SKILL.md")
            if os.path.exists(target):
                try:
                    with open(target, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception:
                    pass
        return None

    def search_online_github(self, skill_name: str) -> Optional[str]:
        """
        Queries online repositories / GitHub raw endpoints for authentic SKILL.md content.
        """
        raw_urls = [
            f"https://raw.githubusercontent.com/anthropics/courses/main/skills/{skill_name}/SKILL.md",
            f"https://raw.githubusercontent.com/awesome-agent-skills/repository/main/{skill_name}/SKILL.md"
        ]
        for url in raw_urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "YORD-Skill-Installer/1.0"})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    if resp.status == 200:
                        return resp.read().decode("utf-8")
            except Exception:
                continue
        return None

    def install_skill(self, skill_name: str, description: str, instructions: str) -> str:
        """
        Creates a new skill package in /skills/<skill_name>/SKILL.md.
        """
        clean_name = re.sub(r'[^a-zA-Z0-9_-]', '', skill_name.lower().replace(" ", "-"))
        skill_path = os.path.join(self.skills_dir, clean_name)
        os.makedirs(skill_path, exist_ok=True)

        md_path = os.path.join(skill_path, "SKILL.md")
        content = f"""---
name: {clean_name}
description: {description}
---

# {skill_name.title()} Skill Package

## Overview
{description}

## Instructions & Domain Directives
{instructions}
"""
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)

        return md_path

    def search_and_install(self, query: str) -> Dict[str, Any]:
        """
        Antigravity-style skill search and auto-installation.
        """
        match = re.search(r'(?:find|install|search)\s+(?:skill\s+)?([a-zA-Z0-9_\-\s]+)', query, re.IGNORECASE)
        skill_target = match.group(1).strip() if match else query.strip()
        clean_name = re.sub(r'[^a-zA-Z0-9_-]', '', skill_target.lower().replace(" ", "-"))

        if self.is_skill_installed(clean_name):
            return {
                "status": "already_installed",
                "skill_name": clean_name,
                "path": os.path.join(self.skills_dir, clean_name, "SKILL.md")
            }

        # 1. Search local global agents skill cache (~/.agents/skills/)
        cached_content = self.search_local_global_skills(clean_name)
        if cached_content:
            target_dir = os.path.join(self.skills_dir, clean_name)
            os.makedirs(target_dir, exist_ok=True)
            installed_path = os.path.join(target_dir, "SKILL.md")
            with open(installed_path, "w", encoding="utf-8") as f:
                f.write(cached_content)
            return {
                "status": "installed_from_cache",
                "skill_name": clean_name,
                "path": installed_path
            }

        # 2. Search GitHub / web online registries
        online_content = self.search_online_github(clean_name)
        if online_content:
            target_dir = os.path.join(self.skills_dir, clean_name)
            os.makedirs(target_dir, exist_ok=True)
            installed_path = os.path.join(target_dir, "SKILL.md")
            with open(installed_path, "w", encoding="utf-8") as f:
                f.write(online_content)
            return {
                "status": "installed_from_web",
                "skill_name": clean_name,
                "path": installed_path
            }

        # 3. Auto-synthesize and install new skill package
        description = f"Autonomous skill for domain: {skill_target}"
        instructions = (
            f"1. Perform deep domain analysis for {skill_target}.\n"
            f"2. Enforce objective, non-sycophantic evaluation.\n"
            f"3. Verify vector citations and structural output bounds."
        )
        installed_path = self.install_skill(clean_name, description, instructions)

        return {
            "status": "auto_synthesized",
            "skill_name": clean_name,
            "path": installed_path
        }

# Global Instance
SKILL_INSTALLER = DynamicSkillInstaller()

"""Skills Manager - Discovers and loads skills from SKILL.md files"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Skill:
    """Represents a skill with its metadata and content"""
    name: str
    description: str
    path: Path
    content: Optional[str] = None
    metadata: Optional[Dict] = None

    def load_full_content(self) -> str:
        """Load the complete skill content"""
        if self.content is None:
            skill_file = self.path / "SKILL.md"
            with open(skill_file, 'r', encoding='utf-8') as f:
                self.content = f.read()
        return self.content


class SkillsManager:
    """Manages skill discovery, loading, and activation"""

    def __init__(self, skills_directory: str = "skills"):
        self.skills_directory = Path(skills_directory)
        self.skills: Dict[str, Skill] = {}
        self._discover_skills()

    def _discover_skills(self):
        """Discover all skills in the skills directory"""
        if not self.skills_directory.exists():
            return

        for item in self.skills_directory.iterdir():
            if item.is_dir():
                skill_file = item / "SKILL.md"
                if skill_file.exists():
                    try:
                        skill = self._parse_skill(skill_file, item)
                        self.skills[skill.name] = skill
                    except Exception as e:
                        print(f"Warning: Failed to load skill from {item}: {e}")

    def _parse_skill(self, skill_file: Path, skill_dir: Path) -> Skill:
        """Parse a SKILL.md file and extract metadata"""
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract YAML frontmatter
        metadata = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1])
                except yaml.YAMLError as e:
                    print(f"Warning: Failed to parse YAML frontmatter: {e}")

        name = metadata.get('name', skill_dir.name)
        description = metadata.get('description', 'No description available')

        return Skill(
            name=name,
            description=description,
            path=skill_dir,
            metadata=metadata
        )

    def get_skills_prompt(self) -> str:
        """Generate XML prompt with available skills for Claude"""
        if not self.skills:
            return ""

        lines = ["<available_skills>"]
        for skill in self.skills.values():
            lines.append("  <skill>")
            lines.append(f"    <name>{skill.name}</name>")
            lines.append(f"    <description>{skill.description}</description>")
            lines.append("  </skill>")
        lines.append("</available_skills>")

        return "\n".join(lines)

    def get_skill_tools(self) -> List[Dict]:
        """Convert skills to OpenAI-style function calling format"""
        tools = []
        for skill in self.skills.values():
            tool = {
                "type": "function",
                "function": {
                    "name": f"activate_skill_{skill.name.replace('-', '_')}",
                    "description": f"Activate the {skill.name} skill. {skill.description}",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "context": {
                                "type": "string",
                                "description": "The context or task details for the skill"
                            }
                        },
                        "required": ["context"]
                    }
                }
            }
            tools.append(tool)
        return tools

    def activate_skill(self, skill_name: str) -> Optional[str]:
        """Activate a skill by loading its full content"""
        skill = self.skills.get(skill_name)
        if skill:
            return skill.load_full_content()
        return None

    def list_skills(self) -> List[Dict[str, str]]:
        """List all available skills with their metadata"""
        return [
            {"name": skill.name, "description": skill.description}
            for skill in self.skills.values()
        ]

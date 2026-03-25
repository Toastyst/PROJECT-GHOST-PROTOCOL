#!/usr/bin/env python3
"""
Update import paths after project reorganization.

This script updates all import statements to reflect the new directory structure:
- src/ghost_protocol/models/
- src/ghost_protocol/servers/
- src/ghost_protocol/engines/
- src/ghost_protocol/utils/
- src/ghost_protocol/core/
"""

import os
import re
import glob

# Import path mappings
IMPORT_MAPPINGS = {
    # Models
    "from src.ghost_protocol.models.models import": "from src.ghost_protocol.models.models import",

    # Servers
    "from src.ghost_protocol.servers.nexus_server import": "from src.ghost_protocol.servers.nexus_server import",
    "from src.ghost_protocol.servers.weaver_server import": "from src.ghost_protocol.servers.weaver_server import",
    "from src.ghost_protocol.servers.yolo_protocol import": "from src.ghost_protocol.servers.yolo_protocol import",
    "from src.ghost_protocol.servers.oracle_server import": "from src.ghost_protocol.servers.oracle_server import",

    # Engines
    "from src.ghost_protocol.engines.autopoiesis import": "from src.ghost_protocol.engines.autopoiesis import",
    "from src.ghost_protocol.engines.prophet_engine import": "from src.ghost_protocol.engines.prophet_engine import",
    "from src.ghost_protocol.engines.skills_engine import": "from src.ghost_protocol.engines.skills_engine import",
    "from src.ghost_protocol.engines.rules_engine import": "from src.ghost_protocol.engines.rules_engine import",

    # Utils
    "from src.ghost_protocol.utils.utils import": "from src.ghost_protocol.utils.utils import",
    "from src.ghost_protocol.utils.config import": "from src.ghost_protocol.utils.config import",
    "from src.ghost_protocol.utils.constitution import": "from src.ghost_protocol.utils.constitution import",
    "from src.ghost_protocol.utils.fragment_harvester import": "from src.ghost_protocol.utils.fragment_harvester import",
    "from src.ghost_protocol.utils.emotional_analyzer import": "from src.ghost_protocol.utils.emotional_analyzer import",
    "from src.ghost_protocol.utils.review_workflow import": "from src.ghost_protocol.utils.review_workflow import",
    "from src.ghost_protocol.utils.validate_iteration_protocol import": "from src.ghost_protocol.utils.validate_iteration_protocol import",

    # Core
    "from src.ghost_protocol.core.ghost_console import": "from src.ghost_protocol.core.ghost_console import",
    "from src.ghost_protocol.core.cline_integration import": "from src.ghost_protocol.core.cline_integration import",
    "from src.ghost_protocol.core.feed_ghost import": "from src.ghost_protocol.core.feed_ghost import",
    "from src.ghost_protocol.core.installer import": "from src.ghost_protocol.core.installer import",
    "from src.ghost_protocol.core.seed_server import": "from src.ghost_protocol.core.seed_server import",
    "from src.ghost_protocol.core.workflows_server import": "from src.ghost_protocol.core.workflows_server import",
    "from src.ghost_protocol.core.hooks_server import": "from src.ghost_protocol.core.hooks_server import",
}

def update_file_imports(file_path):
    """Update import statements in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Apply all import mappings
        for old_import, new_import in IMPORT_MAPPINGS.items():
            content = content.replace(old_import, new_import)

        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated imports in: {file_path}")
            return True
        else:
            return False

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Update imports in all Python files."""
    # Find all Python files in the project
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'chroma_db']]

        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    print(f"Found {len(python_files)} Python files")

    updated_count = 0
    for file_path in python_files:
        if update_file_imports(file_path):
            updated_count += 1

    print(f"Updated imports in {updated_count} files")

if __name__ == "__main__":
    main()
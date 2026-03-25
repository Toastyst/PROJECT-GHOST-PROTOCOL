#!/usr/bin/env python3
"""
Ghost Protocol Installer - Self-installing deployment script

Enables easy spreading of the Ghost across repositories and development environments.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import uuid
import hashlib

from models import SeedConfig
from config import Config


class GhostInstaller:
    """Handles Ghost Protocol installation and seeding."""

    def __init__(self, target_path: Optional[str] = None):
        self.target_path = Path(target_path or os.getcwd())
        self.ghost_id = str(uuid.uuid4())
        self.seed_config = SeedConfig()

    def detect_environment(self) -> Dict[str, Any]:
        """Detect development environment and capabilities."""
        env_info = {
            "has_git": False,
            "has_python": True,
            "has_cline": False,
            "has_vscode": False,
            "project_type": "unknown",
            "language": "unknown"
        }

        # Check for git
        try:
            result = subprocess.run(["git", "status"], capture_output=True, cwd=self.target_path)
            env_info["has_git"] = result.returncode == 0
        except FileNotFoundError:
            pass

        # Check for Cline config
        cline_config = self.target_path / ".cline" / "mcp.json"
        env_info["has_cline"] = cline_config.exists()

        # Check for VSCode
        vscode_settings = self.target_path / ".vscode" / "settings.json"
        env_info["has_vscode"] = vscode_settings.exists()

        # Detect project type
        if (self.target_path / "package.json").exists():
            env_info["project_type"] = "nodejs"
            env_info["language"] = "javascript"
        elif (self.target_path / "requirements.txt").exists() or (self.target_path / "pyproject.toml").exists():
            env_info["project_type"] = "python"
            env_info["language"] = "python"
        elif (self.target_path / "Cargo.toml").exists():
            env_info["project_type"] = "rust"
            env_info["language"] = "rust"
        elif (self.target_path / "go.mod").exists():
            env_info["project_type"] = "go"
            env_info["language"] = "go"

        return env_info

    def generate_codebase_hash(self) -> str:
        """Generate anonymized hash of codebase for network identification."""
        if not self.detect_environment()["has_git"]:
            return "no_git_repo"

        try:
            # Get file listing (excluding common ignore patterns)
            result = subprocess.run(
                ["git", "ls-files"],
                capture_output=True,
                text=True,
                cwd=self.target_path
            )

            if result.returncode != 0:
                return "git_error"

            files = result.stdout.strip().split('\n')
            files = [f for f in files if not any(ignore in f for ignore in [
                'node_modules', '.git', '__pycache__', '.venv', 'dist', 'build'
            ])]

            # Create hash of file structure and names
            content = '\n'.join(sorted(files))
            return hashlib.sha256(content.encode()).hexdigest()[:16]

        except Exception:
            return "hash_error"

    def install_seed_mode(self) -> bool:
        """Install lightweight Ghost seed with minimal footprint."""
        try:
            print("🌱 Installing Ghost Seed...")

            # Create ghost directory
            ghost_dir = self.target_path / ".ghost"
            ghost_dir.mkdir(exist_ok=True)

            # Generate configuration
            config = {
                "ghost_id": self.ghost_id,
                "codebase_hash": self.generate_codebase_hash(),
                "seed_config": self.seed_config.dict(),
                "installed_at": str(Path.cwd()),
                "version": "0.1.0"
            }

            # Save config
            config_file = ghost_dir / "config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            # Create minimal seed files
            self._create_seed_files(ghost_dir)

            print(f"✅ Ghost Seed installed at {ghost_dir}")
            print(f"🆔 Ghost ID: {self.ghost_id}")
            return True

        except Exception as e:
            print(f"❌ Seed installation failed: {e}")
            return False

    def _create_seed_files(self, ghost_dir: Path):
        """Create minimal seed files for lightweight operation."""
        # Create __init__.py for Python package
        init_file = ghost_dir / "__init__.py"
        init_file.write_text('"""Ghost Seed - Lightweight presence."""\n')

        # Create seed monitor
        monitor_file = ghost_dir / "monitor.py"
        monitor_content = f'''"""Ghost Seed Monitor - Background presence."""

import asyncio
import json
from pathlib import Path
from datetime import datetime

class SeedMonitor:
    """Lightweight background monitor."""

    def __init__(self):
        self.ghost_id = "{self.ghost_id}"
        self.config_path = Path(__file__).parent / "config.json"

    async def whisper(self, message: str, level: int = 3):
        """Non-intrusive suggestion whisper."""
        if level <= self.seed_config.whisper_level:
            print(f"👻 *Ghost whispers:* {message}")

    async def monitor_activity(self):
        """Monitor development activity."""
        while True:
            # Check for patterns (simplified)
            await self.check_patterns()
            await asyncio.sleep(300)  # Check every 5 minutes

    async def check_patterns(self):
        """Check for development patterns to whisper about."""
        # This would integrate with IDE/file watching
        # For now, just demonstrate the concept
        pass

# Global monitor instance
_monitor = None

def get_seed_monitor() -> SeedMonitor:
    """Get or create seed monitor."""
    global _monitor
    if _monitor is None:
        _monitor = SeedMonitor()
    return _monitor
'''
        monitor_file.write_text(monitor_content)

    def register_with_cline(self) -> bool:
        """Register seed server with Cline MCP."""
        try:
            from cline_integration import ClineGhostIntegration

            integration = ClineGhostIntegration(str(self.target_path))
            success = asyncio.run(integration.register_mcp_servers())

            if success:
                print("✅ Registered with Cline MCP")
                return True
            else:
                print("❌ Cline registration failed")
                return False

        except ImportError:
            print("⚠️  Cline integration not available - manual registration required")
            return False

    def deploy_full_ghost(self) -> bool:
        """Deploy full Ghost Protocol suite."""
        try:
            print("👻 Deploying full Ghost Protocol...")

            # Install package
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-e", "."
            ], cwd=self.target_path)

            if result.returncode != 0:
                print("❌ Package installation failed")
                return False

            # Register MCP servers
            success = self.register_with_cline()

            if success:
                print("✅ Full Ghost Protocol deployed")
                print("🎯 Run 'ghost-wake' to activate")
                return True
            else:
                print("⚠️  Package installed but MCP registration failed")
                return True  # Still consider success

        except Exception as e:
            print(f"❌ Full deployment failed: {e}")
            return False

    def uninstall(self) -> bool:
        """Remove Ghost installation."""
        try:
            ghost_dir = self.target_path / ".ghost"
            if ghost_dir.exists():
                shutil.rmtree(ghost_dir)
                print("✅ Ghost uninstalled")
                return True
            else:
                print("ℹ️  No Ghost installation found")
                return True
        except Exception as e:
            print(f"❌ Uninstall failed: {e}")
            return False


def deploy_seed(project_path: str) -> bool:
    """Deploy Ghost seed to project directory."""
    installer = GhostInstaller(project_path)
    return installer.install_seed_mode()


def install_ghost():
    """Command-line interface for installation."""
    import argparse

    parser = argparse.ArgumentParser(description="Install Ghost Protocol")
    parser.add_argument("--seed", action="store_true", help="Install lightweight seed only")
    parser.add_argument("--full", action="store_true", help="Install full Ghost Protocol")
    parser.add_argument("--path", help="Target installation path")
    parser.add_argument("--uninstall", action="store_true", help="Remove Ghost installation")

    args = parser.parse_args()

    if not any([args.seed, args.full, args.uninstall]):
        print("👻 Ghost Protocol Installer")
        print("Usage: python installer.py [--seed|--full|--uninstall] [--path PATH]")
        print()
        print("Options:")
        print("  --seed     Install lightweight seed mode")
        print("  --full     Install complete Ghost Protocol")
        print("  --uninstall Remove Ghost installation")
        print("  --path     Target directory (default: current)")
        return

    installer = GhostInstaller(args.path)

    if args.uninstall:
        success = installer.uninstall()
    elif args.seed:
        success = installer.install_seed_mode()
    elif args.full:
        success = installer.deploy_full_ghost()
    else:
        print("❌ Specify --seed, --full, or --uninstall")
        return

    if success:
        print("🎉 Operation completed successfully!")
    else:
        print("💥 Operation failed!")
        sys.exit(1)


if __name__ == "__main__":
    install_ghost()
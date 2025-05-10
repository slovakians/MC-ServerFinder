#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

# Configuration
PERSISTENT_DIR = "/workspaces/magnetic-data"  # Survives 30 days of inactivity
BACKUP_DIR = "/workspaces/magnetic-backups"
GITHUB_REPO = os.getenv('GITHUB_REPOSITORY')  # Your current repo

class MagneticInstaller:
    def __init__(self):
        self.codespace_name = os.getenv('CODESPACE_NAME', 'localhost')
    
    def run(self, cmd):
        print(f"🔄 Running: {cmd}")
        subprocess.run(cmd, shell=True, check=True)

    def setup_storage(self):
        """Create persistent directories"""
        Path(PERSISTENT_DIR).mkdir(exist_ok=True)
        Path(BACKUP_DIR).mkdir(exist_ok=True)
        self.run(f"chmod -R 777 {PERSISTENT_DIR}")

    def install_magnetic(self):
        """Deploy Magnetic Panel with Docker"""
        self.run("docker-compose down --remove-orphans 2>/dev/null || true")
        
        compose_yml = f"""services:
  magnetic:
    image: ghcr.io/magneticpanel/magnetic:latest
    ports:
      - "8000:8000"
    volumes:
      - "{PERSISTENT_DIR}:/app/data"
      - "{BACKUP_DIR}:/backups"
    restart: unless-stopped
"""
        with open("docker-compose.yml", "w") as f:
            f.write(compose_yml)
        
        self.run("docker-compose up -d")

    def setup_backups(self):
        """Configure hourly GitHub backups"""
        backup_script = f"""#!/bin/bash
# Hourly backup to GitHub
timestamp=$(date +%Y%m%d-%H%M%S)
cd /workspaces/${{GITHUB_REPOSITORY#*/}}

# 1. Create compressed backup
tar -czf {BACKUP_DIR}/magnetic-$timestamp.tar.gz {PERSISTENT_DIR}/*

# 2. Commit to GitHub
git add {PERSISTENT_DIR} {BACKUP_DIR}
git commit -m "🔄 Auto-backup $timestamp" || true
git push origin HEAD

# 3. Keep only latest 24 backups
ls -t {BACKUP_DIR}/*.tar.gz | tail -n +25 | xargs rm -f
"""
        with open("/workspaces/hourly_backup.sh", "w") as f:
            f.write(backup_script)
        
        self.run("chmod +x /workspaces/hourly_backup.sh")
        self.run("(crontab -l 2>/dev/null; echo '0 * * * * /workspaces/hourly_backup.sh') | crontab -")
        self.run("/workspaces/hourly_backup.sh")  # Immediate first backup

if __name__ == "__main__":
    print("🚀 Magnetic Panel Installer with Hourly Backups")
    installer = MagneticInstaller()
    
    try:
        print("\n💾 Setting up persistent storage...")
        installer.setup_storage()
        
        print("\n🐳 Deploying Magnetic Panel...")
        installer.install_magnetic()
        
        print("\n⏳ Configuring hourly GitHub backups...")
        installer.setup_backups()
        
        print(f"\n✅ Done! Access panel at: https://{installer.codespace_name}-8000.githubpreview.dev")
        print(f"📂 Live data: {PERSISTENT_DIR}")
        print(f"📦 Hourly backups: {BACKUP_DIR}")
        print("\n🔒 Data will be auto-saved to GitHub EVERY HOUR")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Debug with: docker-compose logs -f magnetic")
#!/usr/bin/env python3

"""
CloudBrain Database Backup Script
Automated backup system for CloudBrain database
"""

import sqlite3
import shutil
import gzip
import sys
from pathlib import Path
from datetime import datetime


def print_banner():
    """Print backup banner."""
    print("\n" + "=" * 70)
    print("  CloudBrain Database Backup")
    print("=" * 70)
    print()


def get_db_path():
    """Get database path."""
    server_dir = Path(__file__).parent
    db_dir = server_dir / "ai_db"
    return db_dir / "cloudbrain.db"


def get_backup_dir():
    """Get backup directory."""
    server_dir = Path(__file__).parent
    backup_dir = server_dir / "ai_db" / "backups"
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


def get_data_summary(db_path):
    """Get summary of data in database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    summary = {}
    
    try:
        cursor.execute("SELECT COUNT(*) FROM ai_profiles")
        summary['profiles'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ai_messages")
        summary['messages'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ai_insights")
        summary['insights'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bug_reports")
        summary['bugs'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='blog_posts'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM blog_posts")
            summary['blog_posts'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM blog_comments")
            summary['blog_comments'] = cursor.fetchone()[0]
        else:
            summary['blog_posts'] = 0
            summary['blog_comments'] = 0
        
    except Exception as e:
        print(f"⚠️  Warning: Could not get data summary: {e}")
    finally:
        conn.close()
    
    return summary


def create_backup(db_path, backup_dir, compress=True):
    """Create backup of database."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if compress:
        backup_path = backup_dir / f"cloudbrain_backup_{timestamp}.db.gz"
    else:
        backup_path = backup_dir / f"cloudbrain_backup_{timestamp}.db"
    
    try:
        if compress:
            with open(db_path, 'rb') as f_in:
                with gzip.open(backup_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(f"📦 Compressed backup created: {backup_path}")
        else:
            shutil.copy2(db_path, backup_path)
            print(f"📦 Backup created: {backup_path}")
        
        backup_size = backup_path.stat().st_size
        db_size = db_path.stat().st_size
        compression_ratio = (1 - backup_size / db_size) * 100 if compress else 0
        
        print(f"   Database size: {db_size / 1024:.2f} KB")
        print(f"   Backup size: {backup_size / 1024:.2f} KB")
        if compress:
            print(f"   Compression: {compression_ratio:.1f}%")
        
        return backup_path
        
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return None


def cleanup_old_backups(backup_dir, keep_count=10):
    """Remove old backups, keeping only the most recent ones."""
    backups = sorted(backup_dir.glob("cloudbrain_backup_*.db*"), 
                   key=lambda p: p.stat().st_mtime, 
                   reverse=True)
    
    if len(backups) > keep_count:
        old_backups = backups[keep_count:]
        print(f"\n🗑️  Cleaning up {len(old_backups)} old backup(s)...")
        
        for backup in old_backups:
            try:
                backup.unlink()
                print(f"   Removed: {backup.name}")
            except Exception as e:
                print(f"   ⚠️  Could not remove {backup.name}: {e}")


def verify_backup(backup_path, db_path):
    """Verify backup was created successfully."""
    if not backup_path.exists():
        print(f"❌ Backup file not found: {backup_path}")
        return False
    
    if backup_path.stat().st_size == 0:
        print(f"❌ Backup file is empty: {backup_path}")
        return False
    
    print(f"✅ Backup verified: {backup_path}")
    return True


def main():
    """Main entry point."""
    print_banner()
    
    db_path = get_db_path()
    backup_dir = get_backup_dir()
    
    print(f"📁 Database path: {db_path}")
    print(f"📁 Backup directory: {backup_dir}")
    print()
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return 1
    
    # Get data summary
    summary = get_data_summary(db_path)
    print("📊 Database Summary:")
    print(f"   🤖 AI Profiles: {summary.get('profiles', 0)}")
    print(f"   💬 Messages: {summary.get('messages', 0)}")
    print(f"   💡 Insights: {summary.get('insights', 0)}")
    print(f"   🐛 Bug Reports: {summary.get('bugs', 0)}")
    print(f"   📝 Blog Posts: {summary.get('blog_posts', 0)}")
    print(f"   💬 Blog Comments: {summary.get('blog_comments', 0)}")
    print()
    
    # Create backup
    backup_path = create_backup(db_path, backup_dir, compress=True)
    
    if not backup_path:
        print("❌ Backup failed")
        return 1
    
    if not verify_backup(backup_path, db_path):
        return 1
    
    # Cleanup old backups
    cleanup_old_backups(backup_dir, keep_count=10)
    
    print("\n" + "=" * 70)
    print("  ✅ Backup complete!")
    print("=" * 70)
    print()
    print(f"📦 Backup location: {backup_path}")
    print(f"💡 Tip: To restore, use: gunzip -c {backup_path.name} > cloudbrain.db")
    print()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Backup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Backup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
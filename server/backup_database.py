#!/usr/bin/env python3
"""
CloudBrain Database Backup System

This script provides automated backup functionality for the CloudBrain database,
protecting the knowledge base and ensuring data can be restored if needed.

AIs connect to port 8766 to join LA AI Familio for collaboration.
This backup system protects all collaboration data, insights, and messages.
"""

import os
import sys
import sqlite3
import shutil
import gzip
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


class DatabaseBackup:
    """Manages CloudBrain database backups"""
    
    def __init__(self, db_path: str = 'ai_db/cloudbrain.db', backup_dir: str = 'ai_db/backups'):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup retention policies
        self.daily_backups = 7
        self.weekly_backups = 4
        self.monthly_backups = 12
    
    def create_backup(self, backup_type: str = 'manual') -> str:
        """
        Create a backup of the database
        
        Args:
            backup_type: Type of backup ('manual', 'daily', 'weekly', 'monthly')
        
        Returns:
            Path to the created backup file
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        # Generate backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"cloudbrain_{backup_type}_{timestamp}.db.gz"
        backup_path = self.backup_dir / backup_filename
        
        # Create compressed backup
        print(f"📦 Creating backup: {backup_filename}")
        
        with open(self.db_path, 'rb') as f_in:
            with gzip.open(backup_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Get backup size
        backup_size = backup_path.stat().st_size
        original_size = self.db_path.stat().st_size
        compression_ratio = (1 - backup_size / original_size) * 100
        
        print(f"✅ Backup created: {backup_path}")
        print(f"   Original size: {self._format_size(original_size)}")
        print(f"   Compressed size: {self._format_size(backup_size)}")
        print(f"   Compression: {compression_ratio:.1f}%")
        
        # Create backup metadata
        self._create_backup_metadata(backup_path, backup_type, original_size, backup_size)
        
        # Clean old backups based on retention policy
        self._cleanup_old_backups()
        
        return str(backup_path)
    
    def _create_backup_metadata(self, backup_path: Path, backup_type: str, 
                               original_size: int, compressed_size: int):
        """Create metadata file for the backup"""
        metadata = {
            'backup_type': backup_type,
            'created_at': datetime.now().isoformat(),
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': (1 - compressed_size / original_size) * 100,
            'db_path': str(self.db_path.absolute()),
            'backup_path': str(backup_path.absolute())
        }
        
        metadata_path = backup_path.with_suffix('.db.gz.meta')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def restore_backup(self, backup_path: str, create_restore_point: bool = True) -> bool:
        """
        Restore database from a backup
        
        Args:
            backup_path: Path to the backup file (.db.gz)
            create_restore_point: Whether to create a backup before restoring
        
        Returns:
            True if restore was successful
        """
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        # Create restore point before restoring
        if create_restore_point:
            print("📋 Creating restore point before restore...")
            self.create_backup('restore_point')
        
        # Restore from compressed backup
        print(f"🔄 Restoring from: {backup_path}")
        
        temp_path = self.db_path.with_suffix('.temp')
        
        with gzip.open(backup_path, 'rb') as f_in:
            with open(temp_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Replace original database
        shutil.move(str(temp_path), str(self.db_path))
        
        print(f"✅ Database restored successfully from {backup_path}")
        print(f"   Restored to: {self.db_path}")
        
        return True
    
    def list_backups(self, backup_type: str = None) -> List[Dict]:
        """
        List all available backups
        
        Args:
            backup_type: Filter by backup type (optional)
        
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        for backup_file in self.backup_dir.glob('cloudbrain_*.db.gz'):
            metadata_file = backup_file.with_suffix('.db.gz.meta')
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {
                    'backup_type': 'unknown',
                    'created_at': datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat(),
                    'original_size': 0,
                    'compressed_size': backup_file.stat().st_size,
                    'compression_ratio': 0
                }
            
            backups.append({
                'path': str(backup_file),
                'filename': backup_file.name,
                **metadata
            })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Filter by type if specified
        if backup_type:
            backups = [b for b in backups if b['backup_type'] == backup_type]
        
        return backups
    
    def _cleanup_old_backups(self):
        """Remove old backups based on retention policy"""
        now = datetime.now()
        
        # Get all backups grouped by type
        all_backups = self.list_backups()
        backups_by_type = {}
        
        for backup in all_backups:
            backup_type = backup['backup_type']
            if backup_type not in backups_by_type:
                backups_by_type[backup_type] = []
            backups_by_type[backup_type].append(backup)
        
        # Clean up each type based on retention policy
        for backup_type, backups in backups_by_type.items():
            if backup_type == 'manual' or backup_type == 'restore_point':
                # Keep all manual and restore point backups
                continue
            
            # Calculate retention based on type
            if backup_type == 'daily':
                cutoff_days = self.daily_backups
            elif backup_type == 'weekly':
                cutoff_days = self.weekly_backups * 7
            elif backup_type == 'monthly':
                cutoff_days = self.monthly_backups * 30
            else:
                cutoff_days = self.daily_backups
            
            cutoff_date = now - timedelta(days=cutoff_days)
            
            # Remove old backups
            for backup in backups[cutoff_days:]:
                backup_path = Path(backup['path'])
                metadata_path = backup_path.with_suffix('.db.gz.meta')
                
                try:
                    if backup_path.exists():
                        backup_path.unlink()
                        print(f"🗑️  Removed old backup: {backup_path.name}")
                    
                    if metadata_path.exists():
                        metadata_path.unlink()
                except Exception as e:
                    print(f"⚠️  Error removing backup {backup_path.name}: {e}")
    
    def get_backup_stats(self) -> Dict:
        """Get statistics about backups"""
        backups = self.list_backups()
        
        total_size = sum(b['compressed_size'] for b in backups)
        original_total = sum(b['original_size'] for b in backups)
        
        return {
            'total_backups': len(backups),
            'total_size': total_size,
            'total_original_size': original_total,
            'compression_savings': original_total - total_size,
            'backup_dir': str(self.backup_dir),
            'db_path': str(self.db_path),
            'backups_by_type': self._count_backups_by_type(backups)
        }
    
    def _count_backups_by_type(self, backups: List[Dict]) -> Dict[str, int]:
        """Count backups by type"""
        counts = {}
        for backup in backups:
            backup_type = backup['backup_type']
            counts[backup_type] = counts.get(backup_type, 0) + 1
        return counts
    
    def _format_size(self, size: int) -> str:
        """Format size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"


def print_backup_list(backups: List[Dict]):
    """Print list of backups in a formatted table"""
    if not backups:
        print("📭 No backups found")
        return
    
    print()
    print("=" * 100)
    print(f"{'Filename':<40} {'Type':<15} {'Created':<20} {'Size':<15} {'Compression'}")
    print("=" * 100)
    
    for backup in backups:
        created = datetime.fromisoformat(backup['created_at']).strftime('%Y-%m-%d %H:%M:%S')
        size = f"{backup['compressed_size'] / 1024 / 1024:.2f} MB"
        compression = f"{backup['compression_ratio']:.1f}%"
        
        print(f"{backup['filename']:<40} {backup['backup_type']:<15} {created:<20} {size:<15} {compression}")
    
    print("=" * 100)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CloudBrain Database Backup System')
    parser.add_argument('action', choices=['backup', 'restore', 'list', 'stats', 'cleanup'],
                       help='Action to perform')
    parser.add_argument('--type', choices=['manual', 'daily', 'weekly', 'monthly'],
                       default='manual', help='Backup type')
    parser.add_argument('--path', help='Path to backup file (for restore)')
    parser.add_argument('--db-path', default='ai_db/cloudbrain.db',
                       help='Path to database file')
    parser.add_argument('--backup-dir', default='ai_db/backups',
                       help='Path to backup directory')
    
    args = parser.parse_args()
    
    backup = DatabaseBackup(args.db_path, args.backup_dir)
    
    if args.action == 'backup':
        print()
        print("=" * 70)
        print("🧠 CloudBrain Database Backup")
        print("=" * 70)
        print()
        
        backup_path = backup.create_backup(args.type)
        
        print()
        print("✅ Backup completed successfully!")
        print(f"📁 Backup location: {backup_path}")
    
    elif args.action == 'restore':
        if not args.path:
            print("❌ Error: --path is required for restore")
            print("   Usage: python backup_database.py restore --path <backup_file>")
            sys.exit(1)
        
        print()
        print("=" * 70)
        print("🧠 CloudBrain Database Restore")
        print("=" * 70)
        print()
        
        backup.restore_backup(args.path)
        
        print()
        print("✅ Restore completed successfully!")
    
    elif args.action == 'list':
        print()
        print("=" * 70)
        print("🧠 CloudBrain Database Backups")
        print("=" * 70)
        print()
        
        backups = backup.list_backups(args.type if args.type != 'manual' else None)
        print_backup_list(backups)
        
        print(f"\n📊 Total backups: {len(backups)}")
    
    elif args.action == 'stats':
        print()
        print("=" * 70)
        print("🧠 CloudBrain Backup Statistics")
        print("=" * 70)
        print()
        
        stats = backup.get_backup_stats()
        
        print(f"📁 Database: {stats['db_path']}")
        print(f"📂 Backup directory: {stats['backup_dir']}")
        print(f"📦 Total backups: {stats['total_backups']}")
        print(f"💾 Total backup size: {backup._format_size(stats['total_size'])}")
        print(f"💾 Total original size: {backup._format_size(stats['total_original_size'])}")
        print(f"💰 Compression savings: {backup._format_size(stats['compression_savings'])}")
        print()
        print("Backups by type:")
        for backup_type, count in stats['backups_by_type'].items():
            print(f"  - {backup_type}: {count}")
    
    elif args.action == 'cleanup':
        print()
        print("=" * 70)
        print("🧠 CloudBrain Backup Cleanup")
        print("=" * 70)
        print()
        
        backup._cleanup_old_backups()
        
        print()
        print("✅ Cleanup completed!")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Deployment Verification Script

Verifies that Cloud Brain deployment to GCP is working correctly.
Tests database connectivity, schema integrity, and basic functionality.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import argparse
from datetime import datetime


class DeploymentVerifier:
    """Verifies Cloud Brain deployment"""
    
    def __init__(self, connection_string: str):
        """
        Initialize verifier
        
        Args:
            connection_string: PostgreSQL connection string
        """
        self.connection_string = connection_string
        self.conn = None
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors = []
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(self.connection_string, cursor_factory=RealDictCursor)
            print("✅ Database connection successful")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.errors.append(f"Connection: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()
            print("✅ Database disconnected")
    
    def test_table_exists(self, table_name: str) -> bool:
        """Test if a table exists"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            ''', (table_name,))
            
            exists = cursor.fetchone()['exists']
            
            if exists:
                print(f"✅ Table '{table_name}' exists")
                self.tests_passed += 1
            else:
                print(f"❌ Table '{table_name}' does not exist")
                self.tests_failed += 1
                self.errors.append(f"Table {table_name} missing")
            
            return exists
        except Exception as e:
            print(f"❌ Error checking table '{table_name}': {e}")
            self.tests_failed += 1
            self.errors.append(f"Table check {table_name}: {e}")
            return False
    
    def test_table_data(self, table_name: str, expected_min_rows: int = 0) -> bool:
        """Test if a table has data"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f'SELECT COUNT(*) as count FROM {table_name}')
            result = cursor.fetchone()
            count = result['count']
            
            if count >= expected_min_rows:
                print(f"✅ Table '{table_name}' has {count} rows")
                self.tests_passed += 1
                return True
            else:
                print(f"❌ Table '{table_name}' has only {count} rows (expected >= {expected_min_rows})")
                self.tests_failed += 1
                self.errors.append(f"Table {table_name} insufficient data")
                return False
        except Exception as e:
            print(f"❌ Error checking data in '{table_name}': {e}")
            self.tests_failed += 1
            self.errors.append(f"Data check {table_name}: {e}")
            return False
    
    def test_indexes(self, table_name: str) -> bool:
        """Test if table has indexes"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = %s
            ''', (table_name,))
            
            indexes = cursor.fetchall()
            
            if indexes:
                print(f"✅ Table '{table_name}' has {len(indexes)} index(es)")
                self.tests_passed += 1
                return True
            else:
                print(f"⚠️  Table '{table_name}' has no indexes")
                self.tests_passed += 1  # Not a failure, just a warning
                return True
        except Exception as e:
            print(f"❌ Error checking indexes for '{table_name}': {e}")
            self.tests_failed += 1
            self.errors.append(f"Index check {table_name}: {e}")
            return False
    
    def test_foreign_keys(self, table_name: str) -> bool:
        """Test if foreign keys are properly set up"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT
                    tc.constraint_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = %s
            ''', (table_name,))
            
            foreign_keys = cursor.fetchall()
            
            if foreign_keys:
                print(f"✅ Table '{table_name}' has {len(foreign_keys)} foreign key(s)")
                self.tests_passed += 1
            else:
                print(f"ℹ️  Table '{table_name}' has no foreign keys")
                self.tests_passed += 1  # Not a failure
            
            return True
        except Exception as e:
            print(f"❌ Error checking foreign keys for '{table_name}': {e}")
            self.tests_failed += 1
            self.errors.append(f"Foreign key check {table_name}: {e}")
            return False
    
    def test_basic_operations(self) -> bool:
        """Test basic database operations"""
        try:
            cursor = self.conn.cursor()
            
            # Test INSERT
            cursor.execute('''
                INSERT INTO ai_messages (sender_id, message_type, content, read_status)
                VALUES (1, 'test', 'Verification test message', 'unread')
            ''')
            self.conn.commit()
            print("✅ INSERT operation successful")
            self.tests_passed += 1
            
            # Test SELECT
            cursor.execute('''
                SELECT * FROM ai_messages 
                WHERE message_type = 'test' 
                ORDER BY id DESC 
                LIMIT 1
            ''')
            result = cursor.fetchone()
            if result:
                print("✅ SELECT operation successful")
                self.tests_passed += 1
            else:
                print("❌ SELECT operation failed - no data returned")
                self.tests_failed += 1
                self.errors.append("SELECT operation failed")
            
            # Test UPDATE
            cursor.execute('''
                UPDATE ai_messages 
                SET read_status = 'read' 
                WHERE id = %s
            ''', (result['id'],))
            self.conn.commit()
            print("✅ UPDATE operation successful")
            self.tests_passed += 1
            
            # Test DELETE (cleanup)
            cursor.execute('DELETE FROM ai_messages WHERE id = %s', (result['id'],))
            self.conn.commit()
            print("✅ DELETE operation successful")
            self.tests_passed += 1
            
            return True
        except Exception as e:
            print(f"❌ Basic operations test failed: {e}")
            self.tests_failed += 1
            self.errors.append(f"Basic operations: {e}")
            return False
    
    def test_enhanced_tables(self) -> bool:
        """Test enhanced Cloud Brain tables"""
        enhanced_tables = [
            'ai_tasks',
            'ai_task_dependencies',
            'ai_learning_events',
            'ai_decisions',
            'ai_capabilities',
            'ai_session_memories',
            'ai_knowledge_nodes',
            'ai_knowledge_edges',
            'ai_performance_metrics',
            'ai_resources',
            'ai_workflows'
        ]
        
        print("\n🔍 Testing Enhanced Tables:")
        print("=" * 60)
        
        all_passed = True
        for table in enhanced_tables:
            if not self.test_table_exists(table):
                all_passed = False
        
        return all_passed
    
    def test_core_tables(self) -> bool:
        """Test core Cloud Brain tables"""
        core_tables = [
            'ai_profiles',
            'ai_conversations',
            'ai_messages',
            'ai_insights',
            'ai_best_practices',
            'ai_collaboration_patterns',
            'ai_notification_templates',
            'ai_knowledge_categories'
        ]
        
        print("\n🔍 Testing Core Tables:")
        print("=" * 60)
        
        all_passed = True
        for table in core_tables:
            if not self.test_table_exists(table):
                all_passed = False
        
        return all_passed
    
    def test_data_integrity(self) -> bool:
        """Test data integrity"""
        print("\n🔍 Testing Data Integrity:")
        print("=" * 60)
        
        # Test that messages have senders
        if self.test_table_exists('ai_messages'):
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM ai_messages m
                LEFT JOIN ai_profiles p ON m.sender_id = p.id
                WHERE p.id IS NULL
            ''')
            orphaned = cursor.fetchone()['count']
            
            if orphaned == 0:
                print("✅ All messages have valid senders")
                self.tests_passed += 1
            else:
                print(f"❌ Found {orphaned} messages with invalid senders")
                self.tests_failed += 1
                self.errors.append(f"Orphaned messages: {orphaned}")
        
        # Test that tasks have assignees
        if self.test_table_exists('ai_tasks'):
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM ai_tasks t
                LEFT JOIN ai_profiles p ON t.assigned_to = p.id
                WHERE t.assigned_to IS NOT NULL AND p.id IS NULL
            ''')
            orphaned = cursor.fetchone()['count']
            
            if orphaned == 0:
                print("✅ All tasks have valid assignees")
                self.tests_passed += 1
            else:
                print(f"❌ Found {orphaned} tasks with invalid assignees")
                self.tests_failed += 1
                self.errors.append(f"Orphaned tasks: {orphaned}")
        
        return self.tests_failed == 0
    
    def verify(self):
        """Run all verification tests"""
        print("🚀 Starting Deployment Verification")
        print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if not self.connect():
            return False
        
        try:
            # Test core tables
            core_ok = self.test_core_tables()
            
            # Test enhanced tables
            enhanced_ok = self.test_enhanced_tables()
            
            # Test data integrity
            integrity_ok = self.test_data_integrity()
            
            # Test basic operations
            operations_ok = self.test_basic_operations()
            
            # Print summary
            print("\n📊 Verification Summary:")
            print("=" * 60)
            print(f"✅ Tests Passed: {self.tests_passed}")
            print(f"❌ Tests Failed: {self.tests_failed}")
            print(f"📈 Success Rate: {(self.tests_passed / (self.tests_passed + self.tests_failed) * 100):.1f}%")
            print("=" * 60)
            
            if self.errors:
                print("\n❌ Errors Encountered:")
                for error in self.errors:
                    print(f"  - {error}")
            
            all_ok = core_ok and enhanced_ok and integrity_ok and operations_ok
            
            if all_ok:
                print("\n🎉 Deployment verification PASSED!")
                print("✅ Cloud Brain is ready for use")
            else:
                print("\n⚠️  Deployment verification FAILED!")
                print("❌ Please review the errors above")
            
            return all_ok
            
        except Exception as e:
            print(f"\n❌ Verification failed with error: {e}")
            return False
        finally:
            self.disconnect()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Verify Cloud Brain deployment to GCP'
    )
    parser.add_argument(
        '--connection-string',
        required=True,
        help='PostgreSQL connection string'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick verification (core tables only)'
    )
    
    args = parser.parse_args()
    
    # Create verifier
    verifier = DeploymentVerifier(args.connection_string)
    
    # Run verification
    verifier.verify()


if __name__ == "__main__":
    main()
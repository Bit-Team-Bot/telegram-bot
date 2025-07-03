#!/usr/bin/env python3
"""
Database Schema Fix Script for Telegram Bot
Adds missing columns and tables to the database
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

def fix_database():
    """Fix the database schema by adding missing columns and tables"""
    
    # Database path
    db_path = Path(__file__).parent.parent / 'telegram_bot.db'
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False
    
    print(f"🔧 Fixing database schema at {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Current user columns: {user_columns}")
        
        # Add missing columns to users table
        missing_user_columns = [
            ("is_superadmin", "BOOLEAN DEFAULT 0"),
            ("is_active", "BOOLEAN DEFAULT 1"),
            ("role", "TEXT DEFAULT 'user'"),
            ("login_code", "TEXT"),
            ("login_code_expires_at", "DATETIME"),
            ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for col_name, col_type in missing_user_columns:
            if col_name not in user_columns:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                    print(f"✅ Added column {col_name} to users table")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"ℹ️ Column {col_name} already exists")
                    else:
                        print(f"❌ Error adding column {col_name}: {e}")
        
        # Check packages table
        cursor.execute("PRAGMA table_info(packages)")
        package_columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Current package columns: {package_columns}")
        
        # Add missing columns to packages table
        missing_package_columns = [
            ("price_usdt", "REAL"),
            ("duration_days", "INTEGER"),
            ("features", "TEXT"),
            ("status", "TEXT DEFAULT 'inactive'"),
            ("start_date", "DATETIME"),
            ("end_date", "DATETIME"),
            ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for col_name, col_type in missing_package_columns:
            if col_name not in package_columns:
                try:
                    cursor.execute(f"ALTER TABLE packages ADD COLUMN {col_name} {col_type}")
                    print(f"✅ Added column {col_name} to packages table")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"ℹ️ Column {col_name} already exists")
                    else:
                        print(f"❌ Error adding column {col_name}: {e}")
        
        # Check payments table
        cursor.execute("PRAGMA table_info(payments)")
        payment_columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Current payment columns: {payment_columns}")
        
        # Add missing columns to payments table
        missing_payment_columns = [
            ("status", "TEXT DEFAULT 'pending'"),
            ("tx_hash", "TEXT UNIQUE"),
            ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
            ("completed_at", "DATETIME"),
            ("cancelled_at", "DATETIME")
        ]
        
        for col_name, col_type in missing_payment_columns:
            if col_name not in payment_columns:
                try:
                    cursor.execute(f"ALTER TABLE payments ADD COLUMN {col_name} {col_type}")
                    print(f"✅ Added column {col_name} to payments table")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"ℹ️ Column {col_name} already exists")
                    else:
                        print(f"❌ Error adding column {col_name}: {e}")
        
        # Create missing tables
        tables_to_create = {
            "features": """
                CREATE TABLE IF NOT EXISTS features (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    code TEXT UNIQUE NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "signal_groups": """
                CREATE TABLE IF NOT EXISTS signal_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    partner_id INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (partner_id) REFERENCES users (id)
                )
            """,
            "partner_permissions": """
                CREATE TABLE IF NOT EXISTS partner_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    partner_id INTEGER UNIQUE,
                    can_manage_users BOOLEAN DEFAULT 0,
                    can_manage_packages BOOLEAN DEFAULT 0,
                    can_manage_payments BOOLEAN DEFAULT 0,
                    can_manage_signal_groups BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (partner_id) REFERENCES users (id)
                )
            """
        }
        
        for table_name, create_sql in tables_to_create.items():
            try:
                cursor.execute(create_sql)
                print(f"✅ Created/verified table {table_name}")
            except sqlite3.OperationalError as e:
                print(f"ℹ️ Table {table_name} already exists or error: {e}")
        
        # Insert default data
        default_packages = [
            (1, 'Basic', 99.0, 30, '["Basic Signals", "1 Group"]', 'active'),
            (2, 'Pro', 299.0, 90, '["Premium Signals", "3 Groups"]', 'active'),
            (3, 'Expert', 599.0, 180, '["Expert Signals", "5 Groups"]', 'active'),
            (4, 'Lifetime', 1999.0, 36500, '["All Features", "Unlimited"]', 'active')
        ]
        
        for package in default_packages:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO packages (id, name, price_usdt, duration_days, features, status) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, package)
                print(f"✅ Added/verified package: {package[1]}")
            except sqlite3.OperationalError as e:
                print(f"ℹ️ Package {package[1]} already exists or error: {e}")
        
        # Setze einen User als Superadmin (anpassen nach Bedarf)
        # cursor.execute("""
        #     UPDATE users 
        #     SET is_superadmin = 1, role = 'superadmin' 
        #     WHERE telegram_id = 'YOUR_TELEGRAM_ID'
        # """)
        # print("✅ Set user YOUR_TELEGRAM_ID as superadmin")
        # if cursor.rowcount == 0:
        #     print("ℹ️ User YOUR_TELEGRAM_ID not found or already superadmin")
        
        # Commit changes
        conn.commit()
        print("✅ Database schema fixed successfully!")
        
        # Show final schema
        print("\n📋 Final database schema:")
        for table in ['users', 'packages', 'payments', 'features', 'signal_groups', 'partner_permissions']:
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                print(f"\n{table}:")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
            except sqlite3.OperationalError:
                print(f"\n{table}: Table not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = fix_database()
    sys.exit(0 if success else 1) 
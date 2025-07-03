-- Fix Database Schema for Telegram Bot
-- Add missing columns to existing tables

-- Add missing columns to users table
ALTER TABLE users ADD COLUMN is_superadmin BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1;
ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user';
ALTER TABLE users ADD COLUMN login_code TEXT;
ALTER TABLE users ADD COLUMN login_code_expires_at DATETIME;
ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Add missing columns to packages table
ALTER TABLE packages ADD COLUMN price_usdt REAL;
ALTER TABLE packages ADD COLUMN duration_days INTEGER;
ALTER TABLE packages ADD COLUMN features TEXT;
ALTER TABLE packages ADD COLUMN status TEXT DEFAULT 'inactive';
ALTER TABLE packages ADD COLUMN start_date DATETIME;
ALTER TABLE packages ADD COLUMN end_date DATETIME;
ALTER TABLE packages ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Add missing columns to payments table
ALTER TABLE payments ADD COLUMN status TEXT DEFAULT 'pending';
ALTER TABLE payments ADD COLUMN tx_hash TEXT UNIQUE;
ALTER TABLE payments ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE payments ADD COLUMN completed_at DATETIME;
ALTER TABLE payments ADD COLUMN cancelled_at DATETIME;

-- Create features table if not exists
CREATE TABLE IF NOT EXISTS features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    code TEXT UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create signal_groups table if not exists
CREATE TABLE IF NOT EXISTS signal_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    partner_id INTEGER,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (partner_id) REFERENCES users (id)
);

-- Create partner_permissions table if not exists
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
);

-- Insert default packages if not exist
INSERT OR IGNORE INTO packages (id, name, price_usdt, duration_days, features, status) VALUES
(1, 'Basic', 99.0, 30, '["Basic Signals", "1 Group"]', 'active'),
(2, 'Pro', 299.0, 90, '["Premium Signals", "3 Groups"]', 'active'),
(3, 'Expert', 599.0, 180, '["Expert Signals", "5 Groups"]', 'active'),
(4, 'Lifetime', 1999.0, 36500, '["All Features", "Unlimited"]', 'active');

-- Insert default features if not exist
INSERT OR IGNORE INTO features (name, code, description) VALUES
('Basic Signals', 'basic_signals', 'Access to basic trading signals'),
('Premium Signals', 'premium_signals', 'Access to premium trading signals'),
('Expert Signals', 'expert_signals', 'Access to expert trading signals'),
('Group Management', 'group_management', 'Manage signal groups'),
('User Management', 'user_management', 'Manage users'),
('Payment Management', 'payment_management', 'Manage payments');

-- Update existing users to have default values
UPDATE users SET is_superadmin = 0 WHERE is_superadmin IS NULL;
UPDATE users SET is_active = 1 WHERE is_active IS NULL;
UPDATE users SET role = 'user' WHERE role IS NULL;

-- Setze einen User als Superadmin (anpassen nach Bedarf)
-- UPDATE users SET is_superadmin = 1, role = 'superadmin' WHERE telegram_id = 'YOUR_TELEGRAM_ID';

-- Show current schema
.schema users
.schema packages
.schema payments 
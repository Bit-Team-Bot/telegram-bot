CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id VARCHAR UNIQUE,
    phone VARCHAR,
    is_superadmin BOOLEAN,
    is_active BOOLEAN,
    role VARCHAR,
    login_code VARCHAR,
    login_code_expires_at TIMESTAMP,
    created_at TIMESTAMP,
    user_name VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    username VARCHAR,
    last_login TIMESTAMP
);
CREATE INDEX ix_users_id ON users (id);

CREATE TABLE package_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE,
    display_name VARCHAR,
    package_type VARCHAR,
    monthly_price DOUBLE PRECISION,
    one_time_price DOUBLE PRECISION,
    features JSONB,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX ix_package_templates_id ON package_templates (id);

CREATE TABLE addons (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE,
    display_name VARCHAR,
    description TEXT,
    monthly_price DOUBLE PRECISION,
    one_time_price DOUBLE PRECISION,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX ix_addons_id ON addons (id);

CREATE TABLE features (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE,
    code VARCHAR UNIQUE,
    description TEXT,
    is_active BOOLEAN,
    created_at TIMESTAMP
);
CREATE INDEX ix_features_id ON features (id);

CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    group_id VARCHAR UNIQUE,
    name VARCHAR,
    settings JSONB,
    welcome_text TEXT,
    night_mode BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX ix_groups_id ON groups (id);

CREATE TABLE scheduled_messages (
    id SERIAL PRIMARY KEY,
    chat_id VARCHAR,
    message_text TEXT NOT NULL,
    schedule_time TIMESTAMP NOT NULL,
    status VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX ix_scheduled_messages_id ON scheduled_messages (id);
CREATE INDEX ix_scheduled_messages_chat_id ON scheduled_messages (chat_id);

CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    text TEXT NOT NULL,
    source VARCHAR,
    category VARCHAR,
    published_at TIMESTAMP,
    created_at TIMESTAMP
);
CREATE INDEX ix_news_id ON news (id);

CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    session_token VARCHAR UNIQUE,
    telegram_id VARCHAR,
    ip_address VARCHAR,
    user_agent VARCHAR,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    last_activity TIMESTAMP
);
CREATE INDEX ix_user_sessions_telegram_id ON user_sessions (telegram_id);
CREATE INDEX ix_user_sessions_id ON user_sessions (id);

CREATE TABLE addon_tiers (
    id SERIAL PRIMARY KEY,
    addon_id INTEGER REFERENCES addons (id),
    level VARCHAR,
    price DOUBLE PRECISION,
    description TEXT,
    is_active BOOLEAN,
    created_at TIMESTAMP
);
CREATE INDEX ix_addon_tiers_id ON addon_tiers (id);

CREATE TABLE package_addons (
    id SERIAL PRIMARY KEY,
    package_template_id INTEGER REFERENCES package_templates (id),
    addon_id INTEGER REFERENCES addons (id),
    is_enabled BOOLEAN,
    created_at TIMESTAMP
);
CREATE INDEX ix_package_addons_id ON package_addons (id);

CREATE TABLE packages (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    price DOUBLE PRECISION,
    duration_days INTEGER,
    features TEXT,
    user_id INTEGER REFERENCES users (id),
    template_id INTEGER REFERENCES package_templates (id),
    status VARCHAR,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP
);
CREATE INDEX ix_packages_id ON packages (id);

CREATE TABLE partner_permissions (
    id SERIAL PRIMARY KEY,
    partner_id INTEGER UNIQUE REFERENCES users (id),
    can_manage_users BOOLEAN,
    can_manage_packages BOOLEAN,
    can_manage_payments BOOLEAN,
    can_manage_signal_groups BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX ix_partner_permissions_id ON partner_permissions (id);

CREATE TABLE userbot_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    session_name VARCHAR NOT NULL,
    session_type VARCHAR NOT NULL,
    phone VARCHAR NOT NULL,
    telegram_session_string TEXT,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    config_data TEXT,
    subscription_status VARCHAR,
    subscription_start_date TIMESTAMP,
    subscription_end_date TIMESTAMP,
    last_payment_date TIMESTAMP,
    next_payment_date TIMESTAMP,
    payment_reminder_sent BOOLEAN,
    deletion_warning_sent BOOLEAN,
    auto_delete_date TIMESTAMP,
    forwarding_enabled BOOLEAN DEFAULT FALSE NOT NULL
);
CREATE INDEX ix_userbot_sessions_id ON userbot_sessions (id);

CREATE TABLE group_user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    group_id INTEGER REFERENCES groups (id),
    role VARCHAR,
    warnings INTEGER,
    mutes INTEGER,
    is_banned BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX ix_group_user_roles_id ON group_user_roles (id);

CREATE TABLE group_warnings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    group_id INTEGER REFERENCES groups (id),
    reason TEXT,
    issued_by INTEGER REFERENCES users (id),
    timestamp TIMESTAMP
);
CREATE INDEX ix_group_warnings_id ON group_warnings (id);

CREATE TABLE group_mutes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    group_id INTEGER REFERENCES groups (id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    reason TEXT,
    issued_by INTEGER REFERENCES users (id),
    active BOOLEAN,
    timestamp TIMESTAMP
);
CREATE INDEX ix_group_mutes_id ON group_mutes (id);

CREATE TABLE coin_analyses (
    id SERIAL PRIMARY KEY,
    coin VARCHAR NOT NULL,
    analysis_text TEXT NOT NULL,
    author_id INTEGER REFERENCES users (id),
    tags VARCHAR,
    rating INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX ix_coin_analyses_id ON coin_analyses (id);

CREATE TABLE source_groups (
    id SERIAL PRIMARY KEY,
    telegram_group_id VARCHAR UNIQUE,
    name VARCHAR,
    owner_id INTEGER REFERENCES users (id),
    topic VARCHAR,
    active BOOLEAN,
    created_at TIMESTAMP
);
CREATE INDEX ix_source_groups_id ON source_groups (id);

CREATE TABLE customer_signal_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    master_group_id VARCHAR,
    package_size INTEGER NOT NULL,
    active BOOLEAN,
    created_at TIMESTAMP,
    expires_at TIMESTAMP
);
CREATE INDEX ix_customer_signal_groups_id ON customer_signal_groups (id);

CREATE TABLE user_addons (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    addon_id INTEGER REFERENCES addons (id),
    tier_id INTEGER REFERENCES addon_tiers (id),
    status VARCHAR,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP
);
CREATE INDEX ix_user_addons_id ON user_addons (id);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    package_id INTEGER REFERENCES packages (id),
    addon_id INTEGER REFERENCES addons (id),
    amount DOUBLE PRECISION,
    status VARCHAR,
    tx_hash VARCHAR UNIQUE,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
CREATE INDEX ix_payments_id ON payments (id);

CREATE TABLE signal_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    description TEXT,
    partner_id INTEGER REFERENCES users (id),
    source_group_id VARCHAR,
    created_group_id VARCHAR,
    created_group_invite_link VARCHAR,
    theme VARCHAR,
    is_active BOOLEAN,
    price_1_group DOUBLE PRECISION,
    price_2_groups DOUBLE PRECISION,
    price_3_groups DOUBLE PRECISION,
    price_4_groups DOUBLE PRECISION,
    price_5_groups DOUBLE PRECISION,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    auto_create_groups BOOLEAN,
    group_prefix VARCHAR,
    max_members_per_group INTEGER,
    auto_forward_messages BOOLEAN,
    forward_delay_seconds INTEGER,
    filter_keywords TEXT,
    exclude_keywords TEXT,
    userbot_session_id INTEGER REFERENCES userbot_sessions (id),
    target_groups TEXT,
    super_group_id VARCHAR,
    themes_config TEXT,
    theme_prices TEXT
);
CREATE INDEX ix_signal_groups_id ON signal_groups (id);

CREATE TABLE topic_assignments (
    id SERIAL PRIMARY KEY,
    source_group_id INTEGER REFERENCES source_groups (id),
    topic_name VARCHAR NOT NULL,
    active BOOLEAN
);
CREATE INDEX ix_topic_assignments_id ON topic_assignments (id);

CREATE TABLE customer_group_topics (
    id SERIAL PRIMARY KEY,
    customer_signal_group_id INTEGER REFERENCES customer_signal_groups (id),
    topic_name VARCHAR NOT NULL,
    price DOUBLE PRECISION,
    active BOOLEAN
);
CREATE INDEX ix_customer_group_topics_id ON customer_group_topics (id);

CREATE TABLE forwarded_messages (
    id SERIAL PRIMARY KEY,
    source_group_id INTEGER REFERENCES source_groups (id),
    target_group_id VARCHAR NOT NULL,
    original_message_id VARCHAR NOT NULL,
    forwarded_message_id VARCHAR,
    user_id INTEGER REFERENCES users (id),
    topic VARCHAR,
    timestamp TIMESTAMP,
    status VARCHAR
);
CREATE INDEX ix_forwarded_messages_id ON forwarded_messages (id);

CREATE TABLE signal_group_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    signal_group_id INTEGER REFERENCES signal_groups (id),
    group_count INTEGER,
    status VARCHAR,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP
);
CREATE INDEX ix_signal_group_subscriptions_id ON signal_group_subscriptions (id);

CREATE TABLE signal_themes (
    id SERIAL PRIMARY KEY,
    signal_group_id INTEGER REFERENCES signal_groups (id),
    name VARCHAR NOT NULL,
    description TEXT,
    keywords TEXT,
    price_monthly DOUBLE PRECISION,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX ix_signal_themes_id ON signal_themes (id);

CREATE TABLE signal_group_theme_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    signal_group_id INTEGER REFERENCES signal_groups (id),
    theme_id INTEGER REFERENCES signal_themes (id),
    status VARCHAR,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    monthly_price DOUBLE PRECISION,
    created_at TIMESTAMP
);
CREATE INDEX ix_signal_group_theme_subscriptions_id ON signal_group_theme_subscriptions (id);

CREATE TABLE alembic_version (
    version_num VARCHAR(32) PRIMARY KEY
);

CREATE TABLE forwarding_group_mappings (
    id SERIAL PRIMARY KEY,
    userbot_session_id INTEGER REFERENCES userbot_sessions (id),
    source_group_id VARCHAR NOT NULL,
    target_group_id VARCHAR NOT NULL,
    forwarding_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX ix_forwarding_group_mappings_id ON forwarding_group_mappings (id);

CREATE TABLE group_kicks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    group_id INTEGER REFERENCES groups (id),
    reason TEXT,
    issued_by INTEGER REFERENCES users (id),
    timestamp TIMESTAMP
);
CREATE INDEX ix_group_kicks_id ON group_kicks (id);

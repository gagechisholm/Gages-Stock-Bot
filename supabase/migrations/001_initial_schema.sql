-- StockNPC Initial Schema
-- Run this in Supabase: Dashboard → SQL Editor → New Query → paste → Run

-- ============================================================
-- Guilds (Discord servers that have added the bot)
-- ============================================================
create table if not exists guilds (
  id                      bigint primary key,        -- Discord guild ID
  name                    text not null,
  owner_id                bigint not null,            -- Discord user ID of server owner
  setup_done              boolean default false,
  premium_tier            text default 'free',        -- 'free' | 'pro' | 'premium'
  stripe_customer_id      text,
  stripe_subscription_id  text,
  discord_entitlement_id  text,
  premium_expires_at      timestamptz,
  created_at              timestamptz default now()
);

-- ============================================================
-- Guild Settings (per-server bot config)
-- ============================================================
create table if not exists guild_settings (
  guild_id          bigint primary key references guilds(id) on delete cascade,
  alert_channel_id  bigint,
  update_channel_id bigint,
  market_open_post  boolean default false,
  market_close_post boolean default false,
  timezone          text default 'America/New_York'
);

-- ============================================================
-- Member Watchlists (personal, per user per server)
-- ============================================================
create table if not exists member_watchlists (
  id         uuid primary key default gen_random_uuid(),
  guild_id   bigint references guilds(id) on delete cascade,
  user_id    bigint not null,                         -- Discord user ID
  symbol     text not null,
  created_at timestamptz default now(),
  unique(guild_id, user_id, symbol)
);

-- ============================================================
-- Server Watchlists (shared, visible to whole server)
-- ============================================================
create table if not exists server_watchlists (
  id         uuid primary key default gen_random_uuid(),
  guild_id   bigint references guilds(id) on delete cascade,
  symbol     text not null,
  added_by   bigint not null,                         -- Discord user ID
  created_at timestamptz default now(),
  unique(guild_id, symbol)
);

-- ============================================================
-- Price Alerts
-- ============================================================
create table if not exists alerts (
  id            uuid primary key default gen_random_uuid(),
  guild_id      bigint references guilds(id) on delete cascade,
  user_id       bigint not null,
  symbol        text not null,
  threshold_pct numeric not null,                     -- e.g. 5.0 = alert at 5% move
  direction     text not null,                        -- 'up' | 'down' | 'both'
  channel_id    bigint not null,                      -- Discord channel to post alert
  active        boolean default true,
  created_at    timestamptz default now()
);

-- ============================================================
-- Paper Portfolios (virtual holdings per user per server)
-- ============================================================
create table if not exists portfolios (
  id         uuid primary key default gen_random_uuid(),
  guild_id   bigint references guilds(id) on delete cascade,
  user_id    bigint not null,
  symbol     text not null,
  shares     numeric not null,
  avg_cost   numeric not null,
  created_at timestamptz default now(),
  unique(guild_id, user_id, symbol)
);

-- ============================================================
-- Trade History (for audit + leaderboard accuracy)
-- ============================================================
create table if not exists trades (
  id          uuid primary key default gen_random_uuid(),
  guild_id    bigint references guilds(id) on delete cascade,
  user_id     bigint not null,
  symbol      text not null,
  action      text not null,                          -- 'buy' | 'sell'
  shares      numeric not null,
  price       numeric not null,
  executed_at timestamptz default now()
);

-- ============================================================
-- Row Level Security (enable on all tables)
-- Service role key bypasses RLS automatically — bot uses this.
-- Anon key (frontend) gets no access by default — safe.
-- ============================================================
alter table guilds              enable row level security;
alter table guild_settings      enable row level security;
alter table member_watchlists   enable row level security;
alter table server_watchlists   enable row level security;
alter table alerts              enable row level security;
alter table portfolios          enable row level security;
alter table trades              enable row level security;

-- ============================================================
-- Indexes for common query patterns
-- ============================================================
create index if not exists idx_member_watchlists_guild_user on member_watchlists(guild_id, user_id);
create index if not exists idx_server_watchlists_guild     on server_watchlists(guild_id);
create index if not exists idx_alerts_active               on alerts(active) where active = true;
create index if not exists idx_alerts_guild_user           on alerts(guild_id, user_id);
create index if not exists idx_portfolios_guild_user       on portfolios(guild_id, user_id);
create index if not exists idx_trades_guild_user           on trades(guild_id, user_id);

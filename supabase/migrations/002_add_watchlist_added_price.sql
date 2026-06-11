-- Add added_price to member_watchlists so the leaderboard can track gain since stock was added
ALTER TABLE member_watchlists ADD COLUMN IF NOT EXISTS added_price numeric;

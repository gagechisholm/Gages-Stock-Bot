<template>
  <main>
    <!-- Hero -->
    <section class="text-center py-24 px-6 bg-gradient-to-b from-gray-900 to-gray-950">
      <p class="text-blue-400 font-semibold text-sm uppercase tracking-widest mb-3">Discord Stock Bot</p>
      <h1 class="text-5xl font-bold text-white mb-5 leading-tight">
        The stock market,<br />inside your Discord server.
      </h1>
      <p class="text-gray-400 text-lg max-w-xl mx-auto mb-8">
        Track stocks, set alerts, run watchlists, and compete on leaderboards — no app downloads,
        no signups for members. Just add the bot and go.
      </p>
      <a
        href="#"
        class="inline-block bg-blue-500 hover:bg-blue-400 text-white font-semibold px-8 py-3 rounded-lg transition-colors text-lg"
      >
        Add to Discord
      </a>
      <p class="text-gray-600 text-sm mt-3">Free to try · No credit card required for members</p>
    </section>

    <!-- Commands preview -->
    <section class="py-16 px-6 bg-gray-950">
      <div class="max-w-3xl mx-auto">
        <h2 class="text-2xl font-bold text-center text-white mb-10">Everything via slash commands</h2>
        <div class="bg-gray-900 rounded-xl border border-gray-800 p-6 font-mono text-sm space-y-3">
          <div class="flex gap-3">
            <span class="text-blue-400">/quote</span>
            <span class="text-gray-400">AAPL</span>
            <span class="text-gray-600 ml-auto">→ AAPL $192.34 ▲ 1.2%</span>
          </div>
          <div class="flex gap-3">
            <span class="text-blue-400">/watchlist</span>
            <span class="text-gray-400">add TSLA</span>
            <span class="text-gray-600 ml-auto">→ Added TSLA to your watchlist</span>
          </div>
          <div class="flex gap-3">
            <span class="text-blue-400">/alert</span>
            <span class="text-gray-400">set NVDA 5% both</span>
            <span class="text-gray-600 ml-auto">→ Alert set for 5% move</span>
          </div>
          <div class="flex gap-3">
            <span class="text-blue-400">/leaderboard</span>
            <span class="text-gray-600 ml-auto">→ 🥇 @user +12.4%</span>
          </div>
          <div class="flex gap-3">
            <span class="text-blue-400">/portfolio</span>
            <span class="text-gray-400">buy SPY 10</span>
            <span class="text-gray-600 ml-auto">→ Bought 10 shares of SPY</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Features grid -->
    <section class="py-16 px-6 bg-gray-950">
      <div class="max-w-5xl mx-auto">
        <h2 class="text-2xl font-bold text-center text-white mb-10">Built for finance communities</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <div class="text-2xl mb-3">📊</div>
            <h3 class="font-bold text-white mb-2">Live Price Lookups</h3>
            <p class="text-gray-400 text-sm">Instant stock quotes from any member, any time, right inside Discord.</p>
          </div>
          <div class="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <div class="text-2xl mb-3">🔔</div>
            <h3 class="font-bold text-white mb-2">Price Movement Alerts</h3>
            <p class="text-gray-400 text-sm">Set a threshold and get notified when a stock moves. Up, down, or both.</p>
          </div>
          <div class="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <div class="text-2xl mb-3">📋</div>
            <h3 class="font-bold text-white mb-2">Personal Watchlists</h3>
            <p class="text-gray-400 text-sm">Every member gets their own watchlist. Add stocks, check prices, track your picks.</p>
          </div>
          <div class="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <div class="text-2xl mb-3">🏆</div>
            <h3 class="font-bold text-white mb-2">Portfolio Leaderboard</h3>
            <p class="text-gray-400 text-sm">Paper-trade with virtual money and compete with other members on the server leaderboard.</p>
          </div>
          <div class="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <div class="text-2xl mb-3">⚙️</div>
            <h3 class="font-bold text-white mb-2">Admin Controls</h3>
            <p class="text-gray-400 text-sm">Set alert channels, manage server settings, and control who can access premium features.</p>
          </div>
          <div class="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <div class="text-2xl mb-3">🔒</div>
            <h3 class="font-bold text-white mb-2">No Investment Advice</h3>
            <p class="text-gray-400 text-sm">Pure market data. No buy/sell signals. No recommendations. Just neutral tools for your community.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="py-20 px-6 text-center">
      <h2 class="text-3xl font-bold text-white mb-4">Ready to activate your server?</h2>
      <p class="text-gray-400 mb-8">Add StockNPC and your members can start using slash commands immediately.</p>
      <a
        href="#"
        class="inline-block bg-blue-500 hover:bg-blue-400 text-white font-semibold px-8 py-3 rounded-lg transition-colors text-lg"
      >
        Add to Discord — It's Free
      </a>
    </section>
  </main>
</template>

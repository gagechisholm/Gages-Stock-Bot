<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <main>

    <!-- HERO -->
    <section class="relative min-h-[88vh] flex flex-col items-center justify-center text-center px-6 py-20 overflow-hidden">
      <!-- subtle grid bg -->
      <div class="absolute inset-0 bg-[#0b0d13]" />
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_-10%,rgba(88,101,242,0.18),transparent)]" />

      <div class="relative z-10 max-w-2xl mx-auto w-full">
        <!-- badge -->
        <div class="inline-flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-4 py-1.5 text-sm text-gray-400 mb-8">
          <span class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span>
          Live in 750+ servers
        </div>

        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-[1.1] tracking-tight mb-5">
          The stock market,
          <span class="text-brand block sm:inline">inside Discord.</span>
        </h1>

        <p class="text-base sm:text-lg text-gray-400 max-w-md mx-auto mb-10 leading-relaxed">
          Price alerts, watchlists, and paper-portfolio competitions.
          All through slash commands. No app downloads. No signups for your members.
        </p>

        <a
          href="https://discord.com/api/oauth2/authorize?client_id=1314311450075861022&permissions=84992&scope=bot+applications.commands"
          target="_blank"
          rel="noopener"
          class="inline-flex items-center gap-3 bg-brand hover:bg-brand-hover text-white font-semibold px-8 py-4 rounded-xl transition-all duration-150 text-lg shadow-[0_0_40px_rgba(88,101,242,0.35)] hover:shadow-[0_0_60px_rgba(88,101,242,0.5)] hover:-translate-y-0.5"
        >
          <svg class="w-6 h-6" viewBox="0 0 71 55" fill="white" xmlns="http://www.w3.org/2000/svg">
            <path d="M60.1 4.9A58.6 58.6 0 0 0 45.6.7a40.7 40.7 0 0 0-1.8 3.7 54.2 54.2 0 0 0-16.3 0A39.7 39.7 0 0 0 25.7.7 58.4 58.4 0 0 0 11.1 4.9C1.6 18.9-1 32.6.3 46.1a59 59 0 0 0 18 9.1 44.6 44.6 0 0 0 3.9-6.3 38.3 38.3 0 0 1-6.1-2.9l1.5-1.1a42.2 42.2 0 0 0 36.1 0l1.5 1.1a38.5 38.5 0 0 1-6.2 2.9 44.2 44.2 0 0 0 3.9 6.3 58.8 58.8 0 0 0 18-9.1C72.2 30.4 68.3 16.8 60.1 4.9ZM23.7 37.9c-3.5 0-6.4-3.2-6.4-7.2s2.8-7.2 6.4-7.2 6.5 3.2 6.4 7.2c0 4-2.8 7.2-6.4 7.2Zm23.6 0c-3.5 0-6.4-3.2-6.4-7.2s2.8-7.2 6.4-7.2 6.4 3.2 6.4 7.2c0 4-2.8 7.2-6.4 7.2Z"/>
          </svg>
          Add to Discord
        </a>

        <p class="mt-4 text-sm text-gray-600">No credit card · Members use it instantly</p>
      </div>
    </section>

    <!-- DISCORD COMMAND PREVIEW -->
    <section class="bg-[#0b0d13] px-6 pb-20">
      <div class="max-w-2xl mx-auto">
        <div class="bg-[#111318] border border-white/[0.06] rounded-2xl overflow-hidden shadow-2xl">
          <!-- fake discord top bar -->
          <div class="flex items-center gap-2 px-4 py-3 border-b border-white/[0.05] bg-[#0d0f14]">
            <div class="w-2.5 h-2.5 rounded-full bg-red-500/60"></div>
            <div class="w-2.5 h-2.5 rounded-full bg-yellow-500/60"></div>
            <div class="w-2.5 h-2.5 rounded-full bg-green-500/60"></div>
            <span class="ml-2 text-xs text-gray-600">#investing · YourServer</span>
          </div>

          <!-- chat messages -->
          <div class="p-5 space-y-4 font-mono text-sm">
            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-brand/30 flex items-center justify-center text-xs text-brand font-bold flex-shrink-0">J</div>
              <div>
                <span class="text-brand font-semibold">jake</span>
                <span class="text-gray-600 text-xs ml-2">today at 9:41am</span>
                <p class="text-gray-300 mt-0.5">/quote AAPL</p>
              </div>
            </div>

            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-[#5865F2]/20 flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4" viewBox="0 0 71 55" fill="#5865F2" xmlns="http://www.w3.org/2000/svg"><path d="M60.1 4.9A58.6 58.6 0 0 0 45.6.7a40.7 40.7 0 0 0-1.8 3.7 54.2 54.2 0 0 0-16.3 0A39.7 39.7 0 0 0 25.7.7 58.4 58.4 0 0 0 11.1 4.9C1.6 18.9-1 32.6.3 46.1a59 59 0 0 0 18 9.1 44.6 44.6 0 0 0 3.9-6.3 38.3 38.3 0 0 1-6.1-2.9l1.5-1.1a42.2 42.2 0 0 0 36.1 0l1.5 1.1a38.5 38.5 0 0 1-6.2 2.9 44.2 44.2 0 0 0 3.9 6.3 58.8 58.8 0 0 0 18-9.1C72.2 30.4 68.3 16.8 60.1 4.9ZM23.7 37.9c-3.5 0-6.4-3.2-6.4-7.2s2.8-7.2 6.4-7.2 6.5 3.2 6.4 7.2c0 4-2.8 7.2-6.4 7.2Zm23.6 0c-3.5 0-6.4-3.2-6.4-7.2s2.8-7.2 6.4-7.2 6.4 3.2 6.4 7.2c0 4-2.8 7.2-6.4 7.2Z"/></svg>
              </div>
              <div>
                <span class="text-white font-semibold">StockNPC</span>
                <span class="text-gray-600 text-xs ml-2">APP</span>
                <div class="mt-1 bg-[#1a1d23] border-l-4 border-brand rounded-r-lg px-3 py-2">
                  <p class="text-white font-semibold">AAPL &nbsp;<span class="text-green-400">$213.49</span></p>
                  <p class="text-gray-400 text-xs mt-0.5">▲ $2.31 &nbsp;+1.09% &nbsp;· &nbsp;Today</p>
                </div>
              </div>
            </div>

            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center text-xs text-purple-400 font-bold flex-shrink-0">S</div>
              <div>
                <span class="text-purple-400 font-semibold">sara</span>
                <span class="text-gray-600 text-xs ml-2">today at 9:43am</span>
                <p class="text-gray-300 mt-0.5">/alert set NVDA 5% both</p>
              </div>
            </div>

            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-[#5865F2]/20 flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4" viewBox="0 0 71 55" fill="#5865F2" xmlns="http://www.w3.org/2000/svg"><path d="M60.1 4.9A58.6 58.6 0 0 0 45.6.7a40.7 40.7 0 0 0-1.8 3.7 54.2 54.2 0 0 0-16.3 0A39.7 39.7 0 0 0 25.7.7 58.4 58.4 0 0 0 11.1 4.9C1.6 18.9-1 32.6.3 46.1a59 59 0 0 0 18 9.1 44.6 44.6 0 0 0 3.9-6.3 38.3 38.3 0 0 1-6.1-2.9l1.5-1.1a42.2 42.2 0 0 0 36.1 0l1.5 1.1a38.5 38.5 0 0 1-6.2 2.9 44.2 44.2 0 0 0 3.9 6.3 58.8 58.8 0 0 0 18-9.1C72.2 30.4 68.3 16.8 60.1 4.9ZM23.7 37.9c-3.5 0-6.4-3.2-6.4-7.2s2.8-7.2 6.4-7.2 6.5 3.2 6.4 7.2c0 4-2.8 7.2-6.4 7.2Zm23.6 0c-3.5 0-6.4-3.2-6.4-7.2s2.8-7.2 6.4-7.2 6.4 3.2 6.4 7.2c0 4-2.8 7.2-6.4 7.2Z"/></svg>
              </div>
              <div>
                <span class="text-white font-semibold">StockNPC</span>
                <span class="text-gray-600 text-xs ml-2">APP</span>
                <p class="text-gray-300 mt-1 text-xs">🔔 Alert set: notify when <span class="text-white">NVDA</span> moves 5% in either direction from <span class="text-white">$875.40</span></p>
              </div>
            </div>

            <!-- leaderboard -->
            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-yellow-500/20 flex items-center justify-center text-xs text-yellow-400 font-bold flex-shrink-0">M</div>
              <div>
                <span class="text-yellow-400 font-semibold">mike</span>
                <span class="text-gray-600 text-xs ml-2">today at 4:02pm</span>
                <p class="text-gray-300 mt-0.5">/leaderboard</p>
              </div>
            </div>
            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-[#5865F2]/20 flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4" viewBox="0 0 71 55" fill="#5865F2" xmlns="http://www.w3.org/2000/svg"><path d="M60.1 4.9A58.6 58.6 0 0 0 45.6.7a40.7 40.7 0 0 0-1.8 3.7 54.2 54.2 0 0 0-16.3 0A39.7 39.7 0 0 0 25.7.7 58.4 58.4 0 0 0 11.1 4.9C1.6 18.9-1 32.6.3 46.1a59 59 0 0 0 18 9.1 44.6 44.6 0 0 0 3.9-6.3 38.3 38.3 0 0 1-6.1-2.9l1.5-1.1a42.2 42.2 0 0 0 36.1 0l1.5 1.1a38.5 38.5 0 0 1-6.2 2.9 44.2 44.2 0 0 0 3.9 6.3 58.8 58.8 0 0 0 18-9.1C72.2 30.4 68.3 16.8 60.1 4.9ZM23.7 37.9c-3.5 0-6.4-3.2-6.4-7.2s2.8-7.2 6.4-7.2 6.5 3.2 6.4 7.2c0 4-2.8 7.2-6.4 7.2Zm23.6 0c-3.5 0-6.4-3.2-6.4-7.2s2.8-7.2 6.4-7.2 6.4 3.2 6.4 7.2c0 4-2.8 7.2-6.4 7.2Z"/></svg>
              </div>
              <div>
                <span class="text-white font-semibold">StockNPC</span>
                <span class="text-gray-600 text-xs ml-2">APP</span>
                <div class="mt-1 bg-[#1a1d23] rounded-lg px-3 py-2 space-y-1 text-xs">
                  <p class="text-yellow-400 font-bold mb-1">📈 Portfolio Leaderboard</p>
                  <p class="text-gray-300">🥇 <span class="text-white">@sara</span> &nbsp;<span class="text-green-400">+18.4%</span></p>
                  <p class="text-gray-300">🥈 <span class="text-white">@jake</span> &nbsp;<span class="text-green-400">+11.2%</span></p>
                  <p class="text-gray-300">🥉 <span class="text-white">@mike</span> &nbsp;<span class="text-green-400">+6.7%</span></p>
                </div>
              </div>
            </div>

            <!-- typing indicator -->
            <div class="text-gray-600 text-xs pl-11">StockNPC is active</div>
          </div>
        </div>
      </div>
    </section>

    <!-- FEATURES -->
    <section class="bg-[#0b0d13] px-6 py-20 border-t border-white/[0.04]">
      <div class="max-w-4xl mx-auto">
        <p class="text-center text-sm text-gray-500 uppercase tracking-widest mb-12">What it does</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-6 hover:border-brand/30 transition-colors">
            <div class="text-2xl mb-3">📊</div>
            <h3 class="font-semibold text-white mb-1">Live Quotes</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Any member can run <code class="text-brand text-xs bg-brand/10 px-1 py-0.5 rounded">/quote AAPL</code> and get the price instantly.</p>
          </div>

          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-6 hover:border-brand/30 transition-colors">
            <div class="text-2xl mb-3">🔔</div>
            <h3 class="font-semibold text-white mb-1">Price Alerts</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Set a move threshold. The bot pings the channel when it triggers. No babysitting required.</p>
          </div>

          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-6 hover:border-brand/30 transition-colors">
            <div class="text-2xl mb-3">📋</div>
            <h3 class="font-semibold text-white mb-1">Personal Watchlists</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Every member gets their own watchlist. Add stocks, check prices, see everything in one command.</p>
          </div>

          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-6 hover:border-brand/30 transition-colors">
            <div class="text-2xl mb-3">🏆</div>
            <h3 class="font-semibold text-white mb-1">Paper Portfolio Leaderboard</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Members paper-trade with virtual money and compete on a live server leaderboard.</p>
          </div>

          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-6 hover:border-brand/30 transition-colors">
            <div class="text-2xl mb-3">⚙️</div>
            <h3 class="font-semibold text-white mb-1">Admin Setup</h3>
            <p class="text-gray-500 text-sm leading-relaxed">One <code class="text-brand text-xs bg-brand/10 px-1 py-0.5 rounded">/setup channel</code> command and the bot is live. No config files, no dashboards.</p>
          </div>

          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-6 hover:border-brand/30 transition-colors">
            <div class="text-2xl mb-3">🔒</div>
            <h3 class="font-semibold text-white mb-1">No Investment Advice</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Pure market data. Neutral tool. No buy/sell signals. Safe for any finance community.</p>
          </div>

        </div>
      </div>
    </section>

    <!-- BOTTOM CTA -->
    <section class="bg-[#0b0d13] px-6 py-24 text-center border-t border-white/[0.04]">
      <div class="max-w-xl mx-auto">
        <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4 tracking-tight">
          Get it running in 60 seconds.
        </h2>
        <p class="text-gray-500 mb-10">
          Add the bot, run <code class="text-brand bg-brand/10 px-1.5 py-0.5 rounded text-sm">/setup channel #your-channel</code>, done.
          Your members can start using it immediately.
        </p>
        <a
          href="https://discord.com/api/oauth2/authorize?client_id=1314311450075861022&permissions=84992&scope=bot+applications.commands"
          target="_blank"
          rel="noopener"
          class="inline-flex items-center gap-3 bg-brand hover:bg-brand-hover text-white font-semibold px-8 py-4 rounded-xl transition-all duration-150 text-lg shadow-[0_0_40px_rgba(88,101,242,0.3)] hover:shadow-[0_0_60px_rgba(88,101,242,0.45)] hover:-translate-y-0.5"
        >
          <svg class="w-6 h-6" viewBox="0 0 71 55" fill="white" xmlns="http://www.w3.org/2000/svg">
            <path d="M60.1 4.9A58.6 58.6 0 0 0 45.6.7a40.7 40.7 0 0 0-1.8 3.7 54.2 54.2 0 0 0-16.3 0A39.7 39.7 0 0 0 25.7.7 58.4 58.4 0 0 0 11.1 4.9C1.6 18.9-1 32.6.3 46.1a59 59 0 0 0 18 9.1 44.6 44.6 0 0 0 3.9-6.3 38.3 38.3 0 0 1-6.1-2.9l1.5-1.1a42.2 42.2 0 0 0 36.1 0l1.5 1.1a38.5 38.5 0 0 1-6.2 2.9 44.2 44.2 0 0 0 3.9 6.3 58.8 58.8 0 0 0 18-9.1C72.2 30.4 68.3 16.8 60.1 4.9ZM23.7 37.9c-3.5 0-6.4-3.2-6.4-7.2s2.8-7.2 6.4-7.2 6.5 3.2 6.4 7.2c0 4-2.8 7.2-6.4 7.2Zm23.6 0c-3.5 0-6.4-3.2-6.4-7.2s2.8-7.2 6.4-7.2 6.4 3.2 6.4 7.2c0 4-2.8 7.2-6.4 7.2Z"/>
          </svg>
          Add to Discord
        </a>
        <p class="mt-4 text-sm text-gray-600">Free tier · Upgrade anytime for premium features</p>
      </div>
    </section>

  </main>
</template>

<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <main>

    <!-- HERO -->
    <section class="relative min-h-[90vh] flex flex-col items-center justify-center text-center px-6 py-20 overflow-hidden">
      <div class="absolute inset-0 bg-[#0b0d13]" />
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_-10%,rgba(88,101,242,0.18),transparent)]" />

      <div class="relative z-10 max-w-2xl mx-auto w-full">
        <div class="inline-flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-4 py-1.5 text-sm text-gray-400 mb-8">
          <span class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span>
          Free for your server &bull; Pro from $5/mo
        </div>

        <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white leading-[1.08] tracking-tight mb-5">
          The Discord bot that
          <span class="text-brand block">roasts your friends' stock picks.</span>
        </h1>

        <p class="text-base sm:text-lg text-gray-400 max-w-xl mx-auto mb-9 leading-relaxed">
          Everyone adds their picks. The bot ranks the whole server every market close,
          then publicly praises the winners and roasts the losers. Daily.
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

        <p class="mt-4 text-sm text-gray-600">Free to add &bull; No account &bull; Live in 60 seconds</p>

        <!-- trust strip (truthful, non-numeric) -->
        <div class="mt-10 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs text-gray-600">
          <span class="flex items-center gap-1.5"><span class="text-green-400">&check;</span> Works in any server</span>
          <span class="flex items-center gap-1.5"><span class="text-green-400">&check;</span> No login, no setup forms</span>
          <span class="flex items-center gap-1.5"><span class="text-green-400">&check;</span> Real market data</span>
          <span class="flex items-center gap-1.5"><span class="text-green-400">&check;</span> AI roasts every market close</span>
        </div>
      </div>
    </section>

    <!-- DISCORD PREVIEW -->
    <section class="bg-[#0b0d13] px-6 pb-20">
      <div class="max-w-2xl mx-auto">
        <p class="text-center text-sm text-gray-500 mb-5">This is what drops in your server at 4:05 PM. Automatically.</p>
        <div class="bg-[#111318] border border-white/[0.06] rounded-2xl overflow-hidden shadow-2xl">
          <div class="flex items-center gap-2 px-4 py-3 border-b border-white/[0.05] bg-[#0d0f14]">
            <div class="w-2.5 h-2.5 rounded-full bg-red-500/60"></div>
            <div class="w-2.5 h-2.5 rounded-full bg-yellow-500/60"></div>
            <div class="w-2.5 h-2.5 rounded-full bg-green-500/60"></div>
            <span class="ml-2 text-xs text-gray-600">#stocks &bull; the-boys-server</span>
          </div>

          <div class="p-5 space-y-4 font-mono text-sm">

            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-[#5865F2]/20 flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4" viewBox="0 0 71 55" fill="#5865F2" xmlns="http://www.w3.org/2000/svg"><path d="M60.1 4.9A58.6 58.6 0 0 0 45.6.7a40.7 40.7 0 0 0-1.8 3.7 54.2 54.2 0 0 0-16.3 0A39.7 39.7 0 0 0 25.7.7 58.4 58.4 0 0 0 11.1 4.9C1.6 18.9-1 32.6.3 46.1a59 59 0 0 0 18 9.1 44.6 44.6 0 0 0 3.9-6.3 38.3 38.3 0 0 1-6.1-2.9l1.5-1.1a42.2 42.2 0 0 0 36.1 0l1.5 1.1a38.5 38.5 0 0 1-6.2 2.9 44.2 44.2 0 0 0 3.9 6.3 58.8 58.8 0 0 0 18-9.1C72.2 30.4 68.3 16.8 60.1 4.9ZM23.7 37.9c-3.5 0-6.4-3.2-6.4-7.2s2.8-7.2 6.4-7.2 6.5 3.2 6.4 7.2c0 4-2.8 7.2-6.4 7.2Zm23.6 0c-3.5 0-6.4-3.2-6.4-7.2s2.8-7.2 6.4-7.2 6.4 3.2 6.4 7.2c0 4-2.8 7.2-6.4 7.2Z"/></svg>
              </div>
              <div class="flex-1">
                <span class="text-white font-semibold">StockNPC</span>
                <span class="text-gray-600 text-xs ml-2">APP &bull; Today at 4:05 PM</span>
                <div class="mt-1.5 text-xs space-y-2 leading-relaxed">
                  <p class="text-gray-400">market closed. let&apos;s see who ate and who&apos;s coping &#128202;</p>
                  <p class="text-gray-200">
                    &#127942; <span class="text-yellow-300 font-semibold">Henry</span>
                    <span class="text-green-400 font-semibold"> +21%</span>
                    <span class="text-gray-400"> portfolio looks like a money glitch. take the victory lap &#128176;&#127950;&#65039;</span>
                  </p>
                  <p class="text-gray-200">
                    &#129352; <span class="text-white font-semibold">Josh</span>
                    <span class="text-green-400 font-semibold"> +11%</span>
                    <span class="text-gray-400"> respectable gains. not enough to catch Henry, but enough to dodge a roast this week</span>
                  </p>
                  <p class="text-gray-200">
                    &#129353; <span class="text-white font-semibold">Enrique</span>
                    <span class="text-red-400 font-semibold"> -1%</span>
                    <span class="text-gray-400"> basically invested in a savings account and still lost his wallet &#128512;</span>
                  </p>
                  <p class="text-gray-200">
                    &#128128; <span class="text-red-400 font-semibold">Jared</span>
                    <span class="text-red-400 font-semibold"> -45%</span>
                    <span class="text-gray-400"> bro turned rent money into a limited edition collectible. down 45% is speedrunning generational debt, absolutely TERRIBLE work &#128201;&#128293;</span>
                  </p>
                </div>
              </div>
            </div>

            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center text-xs text-red-400 font-bold flex-shrink-0">J</div>
              <div>
                <span class="text-red-400 font-semibold">Jared</span>
                <span class="text-gray-600 text-xs ml-2">4:05 PM</span>
                <p class="text-gray-300 mt-0.5">bro I hate this bot so much</p>
              </div>
            </div>

            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-full bg-yellow-500/20 flex items-center justify-center text-xs text-yellow-300 font-bold flex-shrink-0">H</div>
              <div>
                <span class="text-yellow-300 font-semibold">Henry</span>
                <span class="text-gray-600 text-xs ml-2">4:06 PM</span>
                <p class="text-gray-300 mt-0.5">&#128176;&#128176;&#128176;</p>
              </div>
            </div>

            <div class="text-gray-600 text-xs pl-11">StockNPC is active</div>
          </div>
        </div>
        <p class="text-center text-sm text-gray-600 mt-5">
          Plus a <code class="text-brand text-xs bg-brand/10 px-1 py-0.5 rounded">/roast @friend</code> command, for when it can&apos;t wait until 4 PM.
        </p>
      </div>
    </section>

    <!-- HOW IT WORKS -->
    <section class="bg-[#0b0d13] px-6 py-20 border-t border-white/[0.04]">
      <div class="max-w-4xl mx-auto">
        <p class="text-center text-sm text-gray-500 uppercase tracking-widest mb-3">Live in 60 seconds</p>
        <h2 class="text-center text-2xl sm:text-3xl font-bold text-white mb-12 tracking-tight">
          Three steps. No account. No credit card.
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-6">
            <div class="text-brand font-bold text-sm mb-2">STEP 1</div>
            <h3 class="font-semibold text-white mb-1">Add the bot</h3>
            <p class="text-gray-500 text-sm leading-relaxed">One click. It lands in your server like any other Discord bot.</p>
          </div>
          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-6">
            <div class="text-brand font-bold text-sm mb-2">STEP 2</div>
            <h3 class="font-semibold text-white mb-1">Pick a channel</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Run <code class="text-brand text-xs bg-brand/10 px-1 py-0.5 rounded">/setup channel #stocks</code> so the bot knows where to post.</p>
          </div>
          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-6">
            <div class="text-brand font-bold text-sm mb-2">STEP 3</div>
            <h3 class="font-semibold text-white mb-1">Everyone picks stocks</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Members add picks with <code class="text-brand text-xs bg-brand/10 px-1 py-0.5 rounded">/watchlist add</code>. The leaderboard does the rest.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- WHAT IT DOES -->
    <section class="bg-[#0b0d13] px-6 py-20 border-t border-white/[0.04]">
      <div class="max-w-4xl mx-auto">
        <p class="text-center text-sm text-gray-500 uppercase tracking-widest mb-3">What it does</p>
        <h2 class="text-center text-2xl sm:text-3xl font-bold text-white mb-12 tracking-tight">
          Simple enough that anyone in the server can use it.
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-6 hover:border-brand/30 transition-colors">
            <div class="text-2xl mb-3">&#127942;</div>
            <h3 class="font-semibold text-white mb-1">The daily roast leaderboard</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Every market close, AI ranks everyone in the server and roasts them publicly. Daily, weekly, and monthly.</p>
          </div>

          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-6 hover:border-brand/30 transition-colors">
            <div class="text-2xl mb-3">&#128293;</div>
            <h3 class="font-semibold text-white mb-1">Roast a friend on demand</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Run <code class="text-brand text-xs bg-brand/10 px-1 py-0.5 rounded">/roast @friend</code> and the bot tears their picks apart, using the live leaderboard for ammo.</p>
          </div>

          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-6 hover:border-brand/30 transition-colors">
            <div class="text-2xl mb-3">&#128203;</div>
            <h3 class="font-semibold text-white mb-1">Track your picks</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Add stocks to your watchlist. The bot tracks your gain from the day you added them. See who&apos;s actually up.</p>
          </div>

          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-6 hover:border-brand/30 transition-colors">
            <div class="text-2xl mb-3">&#128276;</div>
            <h3 class="font-semibold text-white mb-1">Get pings. Don&apos;t miss it.</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Set a percentage threshold on any stock. The bot pings the channel when it moves. No babysitting required.</p>
          </div>

          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-6 hover:border-brand/30 transition-colors">
            <div class="text-2xl mb-3">&#128202;</div>
            <h3 class="font-semibold text-white mb-1">Check any price, instantly</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Run <code class="text-brand text-xs bg-brand/10 px-1 py-0.5 rounded">/quote AAPL</code> and get the price. No apps. No accounts. Works for anyone in the server.</p>
          </div>

          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-6 hover:border-brand/30 transition-colors">
            <div class="text-2xl mb-3">&#128184;</div>
            <h3 class="font-semibold text-white mb-1">Not $125/month</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Serious trading bots cost serious money. StockNPC is free to add, and Pro is $5/mo. An impulse buy, not a business decision.</p>
          </div>

        </div>
      </div>
    </section>

    <!-- PRICING -->
    <section class="bg-[#0b0d13] px-6 py-20 border-t border-white/[0.04]">
      <div class="max-w-3xl mx-auto">
        <h2 class="text-center text-2xl sm:text-3xl font-bold text-white mb-3 tracking-tight">
          Free to add. $5 when your server wants more.
        </h2>
        <p class="text-center text-gray-500 mb-12">No account, no credit card to start. Upgrade only if you want the daily chaos.</p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="bg-[#111318] border border-white/[0.06] rounded-2xl p-7">
            <h3 class="text-white font-semibold text-lg mb-1">Free</h3>
            <div class="text-3xl font-extrabold text-white mb-5">$0</div>
            <ul class="space-y-2.5 text-sm text-gray-400">
              <li><span class="text-green-400">&check;</span> Live prices with <code class="text-brand text-xs bg-brand/10 px-1 py-0.5 rounded">/quote</code></li>
              <li><span class="text-green-400">&check;</span> 5 stocks per watchlist</li>
              <li><span class="text-green-400">&check;</span> 3 price alerts each</li>
              <li><span class="text-green-400">&check;</span> 2 <code class="text-brand text-xs bg-brand/10 px-1 py-0.5 rounded">/roast</code> uses a week</li>
              <li><span class="text-green-400">&check;</span> On-demand leaderboard</li>
            </ul>
          </div>

          <div class="bg-[#111318] border border-brand/50 rounded-2xl p-7 relative shadow-[0_0_50px_rgba(88,101,242,0.18)]">
            <span class="absolute -top-3 left-7 bg-brand text-white text-xs font-bold px-3 py-1 rounded-full">MOST FUN</span>
            <h3 class="text-white font-semibold text-lg mb-1">Pro</h3>
            <div class="text-3xl font-extrabold text-white mb-5">$5<span class="text-base font-medium text-gray-500">/mo</span></div>
            <ul class="space-y-2.5 text-sm text-gray-300">
              <li><span class="text-green-400">&check;</span> <span class="text-white font-medium">Daily auto roast leaderboard</span> at every market close</li>
              <li><span class="text-green-400">&check;</span> Weekly + monthly recaps</li>
              <li><span class="text-green-400">&check;</span> Unlimited watchlist picks</li>
              <li><span class="text-green-400">&check;</span> Unlimited alerts</li>
              <li><span class="text-green-400">&check;</span> Unlimited <code class="text-brand text-xs bg-brand/10 px-1 py-0.5 rounded">/roast</code></li>
            </ul>
          </div>
        </div>
        <p class="text-center text-xs text-gray-600 mt-5">Billed monthly. Cancel anytime. Upgrade from inside Discord with <code class="text-brand text-xs bg-brand/10 px-1 py-0.5 rounded">/upgrade</code>.</p>
      </div>
    </section>

    <!-- BOTTOM CTA -->
    <section class="bg-[#0b0d13] px-6 py-24 text-center border-t border-white/[0.04]">
      <div class="max-w-xl mx-auto">
        <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4 tracking-tight">
          Your boys are talking about stocks anyway.
        </h2>
        <p class="text-gray-500 mb-10 text-lg">
          Might as well rank them and let the bot do the trash talk.
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
        <p class="mt-4 text-sm text-gray-600">Free to add &bull; No account &bull; Live in 60 seconds</p>
      </div>
    </section>

  </main>
</template>

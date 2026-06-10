<template>
  <main class="max-w-3xl mx-auto px-6 py-16">
    <h1 class="text-3xl font-bold text-white mb-2">Privacy Policy</h1>
    <p class="text-gray-500 text-sm mb-10">Last updated: June 10, 2026</p>

    <div class="prose prose-invert space-y-8 text-gray-300 leading-relaxed">

      <section>
        <h2 class="text-xl font-semibold text-white mb-3">1. Who we are</h2>
        <p>
          StockNPC ("we", "our", "the bot") is a Discord application that provides stock market
          data tools for Discord servers. We are not a financial services provider, broker, or
          investment adviser.
        </p>
      </section>

      <section>
        <h2 class="text-xl font-semibold text-white mb-3">2. What data we collect</h2>
        <p>When you use StockNPC, we collect and store the following:</p>
        <ul class="list-disc list-inside mt-3 space-y-2 text-gray-400">
          <li><strong class="text-gray-200">Discord Guild ID</strong> — the unique identifier of your Discord server, used to associate settings and watchlists with your server.</li>
          <li><strong class="text-gray-200">Discord User ID</strong> — your unique Discord user identifier, used to associate your watchlist, alerts, and paper portfolio with your account.</li>
          <li><strong class="text-gray-200">Stock symbols</strong> — the ticker symbols you add to your watchlists or alerts.</li>
          <li><strong class="text-gray-200">Paper portfolio data</strong> — virtual share quantities and average cost used for the leaderboard feature.</li>
          <li><strong class="text-gray-200">Alert preferences</strong> — your configured price alert thresholds and directions.</li>
          <li><strong class="text-gray-200">Server settings</strong> — channel IDs and configuration set by server administrators.</li>
        </ul>
        <p class="mt-3">
          We do not collect your real name, email address, real brokerage accounts, or any financial
          account information. We do not read the content of your messages beyond the slash commands
          you explicitly send to the bot.
        </p>
      </section>

      <section>
        <h2 class="text-xl font-semibold text-white mb-3">3. How we use your data</h2>
        <p>We use the data listed above exclusively to:</p>
        <ul class="list-disc list-inside mt-3 space-y-2 text-gray-400">
          <li>Display your watchlist and portfolio when you request it</li>
          <li>Trigger price movement alerts to the configured server channel</li>
          <li>Calculate and display the server leaderboard</li>
          <li>Store server configuration set by administrators</li>
          <li>Determine subscription/premium status for feature gating</li>
        </ul>
        <p class="mt-3">
          We do not sell, rent, or share your data with third parties for advertising or marketing purposes.
        </p>
      </section>

      <section>
        <h2 class="text-xl font-semibold text-white mb-3">4. Third-party services</h2>
        <p>StockNPC uses the following third-party services to operate:</p>
        <ul class="list-disc list-inside mt-3 space-y-2 text-gray-400">
          <li><strong class="text-gray-200">Discord</strong> — the platform the bot operates on. Discord's own Privacy Policy governs how Discord handles your account data.</li>
          <li><strong class="text-gray-200">Marketstack</strong> — provides stock price data. Ticker symbols you look up may be sent to Marketstack's API. See Marketstack's privacy policy for details.</li>
          <li><strong class="text-gray-200">Supabase</strong> — our database provider. Your data is stored in Supabase-hosted PostgreSQL databases in a secure environment.</li>
          <li><strong class="text-gray-200">Stripe (for paid plans)</strong> — payment processing for server subscriptions. Stripe handles all payment data; we never see or store credit card information.</li>
        </ul>
      </section>

      <section>
        <h2 class="text-xl font-semibold text-white mb-3">5. Data retention</h2>
        <p>
          We retain your data for as long as the bot is active in your server or you have an active
          account. If you remove the bot from your server, your server's data may be retained for up
          to 90 days before deletion.
        </p>
      </section>

      <section>
        <h2 class="text-xl font-semibold text-white mb-3">6. Your rights and data deletion</h2>
        <p>
          You have the right to request deletion of your personal data at any time. To request deletion:
        </p>
        <ul class="list-disc list-inside mt-3 space-y-2 text-gray-400">
          <li>Join our support server and open a support ticket, or</li>
          <li>Email us at the contact address below</li>
        </ul>
        <p class="mt-3">
          We will process deletion requests within 30 days. Note that server administrators can only
          request deletion of server-level data (watchlists, settings). Individual members can request
          deletion of their own user-level data (personal watchlist, alerts, portfolio).
        </p>
      </section>

      <section>
        <h2 class="text-xl font-semibold text-white mb-3">7. Children's privacy</h2>
        <p>
          StockNPC is not directed at children under 13. We do not knowingly collect data from
          anyone under 13. Discord's minimum age requirement applies.
        </p>
      </section>

      <section>
        <h2 class="text-xl font-semibold text-white mb-3">8. Changes to this policy</h2>
        <p>
          We may update this Privacy Policy periodically. When we do, we will update the "Last updated"
          date at the top. Continued use of the bot after changes constitutes acceptance of the updated policy.
        </p>
      </section>

      <section>
        <h2 class="text-xl font-semibold text-white mb-3">9. Contact</h2>
        <p>
          For privacy questions, data requests, or to report concerns, contact us through our Discord
          support server or by email. Links are available on the bot's Discord profile page.
        </p>
      </section>

    </div>
  </main>
</template>

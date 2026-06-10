<template>
  <div class="bg-[#0b0d13] text-gray-200 min-h-screen flex flex-col">
    <nav class="bg-[#0b0d13]/80 backdrop-blur-md border-b border-white/[0.06] px-6 py-4 sticky top-0 z-50">
      <div class="max-w-5xl mx-auto flex justify-between items-center">
        <router-link to="/" class="flex items-center gap-2.5">
          <img src="/stocknpc-logo.svg" alt="" class="w-9 h-9 object-contain" />
          <span class="text-xl font-bold tracking-tight">
            <span class="text-white">Stock</span><span class="text-green-400">NPC</span>
          </span>
        </router-link>
        <div class="flex gap-6 text-sm text-gray-400">
          <router-link to="/privacy" class="hover:text-gray-200 transition-colors">Privacy</router-link>
          <router-link to="/terms" class="hover:text-gray-200 transition-colors">Terms</router-link>
        </div>
      </div>
    </nav>

    <div class="flex-1">
      <router-view />
    </div>

    <footer class="bg-[#0b0d13] border-t border-white/[0.06] px-6 py-6 text-center text-sm text-gray-600">
      <div class="flex justify-center gap-6 mb-2">
        <router-link to="/privacy" class="hover:text-gray-300 transition-colors">Privacy Policy</router-link>
        <router-link to="/terms" class="hover:text-gray-300 transition-colors">Terms of Service</router-link>
      </div>
      <p>&copy; {{ new Date().getFullYear() }} StockNPC &ndash; ChairLink LLC. All rights reserved.</p>
      <p class="mt-1">Not financial advice. For entertainment and engagement purposes only.</p>
    </footer>
  </div>
</template>

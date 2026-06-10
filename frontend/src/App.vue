<template>
  <div class="bg-gray-950 text-gray-200 min-h-screen flex flex-col">
    <nav class="bg-gray-900 border-b border-gray-800 px-6 py-4 sticky top-0 z-10">
      <div class="max-w-5xl mx-auto flex justify-between items-center">
        <router-link to="/" class="text-xl font-bold text-blue-400">StockNPC</router-link>
        <div class="flex gap-6 text-sm text-gray-400">
          <router-link to="/privacy" class="hover:text-gray-200 transition-colors">Privacy</router-link>
          <router-link to="/terms" class="hover:text-gray-200 transition-colors">Terms</router-link>
        </div>
      </div>
    </nav>

    <div class="flex-1">
      <router-view />
    </div>

    <footer class="bg-gray-900 border-t border-gray-800 px-6 py-6 text-center text-sm text-gray-500">
      <div class="flex justify-center gap-6 mb-2">
        <router-link to="/privacy" class="hover:text-gray-300 transition-colors">Privacy Policy</router-link>
        <router-link to="/terms" class="hover:text-gray-300 transition-colors">Terms of Service</router-link>
      </div>
      <p>&copy; {{ new Date().getFullYear() }} StockNPC. All rights reserved.</p>
      <p class="mt-1">Not financial advice. For entertainment and engagement purposes only.</p>
    </footer>
  </div>
</template>

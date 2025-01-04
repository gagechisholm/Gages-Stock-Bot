<template>
  <div class="bg-primary text-gray-200 min-h-screen">
    <!-- Navbar -->
    <nav class="bg-primary p-4 sticky top-0 z-10 shadow-lg">
      <div class="container mx-auto flex justify-between items-center">
        <h1 class="text-2xl font-bold text-accent">StockBot</h1>
        <ul class="flex space-x-6">
          <li><a href="#home" class="hover:text-accent">Home</a></li>
          <li><a href="#logs" class="hover:text-accent">Logs</a></li>
          <li><a href="#features" class="hover:text-accent">Features</a></li>
          <li><a href="#contact" class="hover:text-accent">Contact</a></li>
        </ul>
      </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="text-center py-20 bg-gradient-to-b from-gray-800 to-primary">
      <h2 class="text-4xl font-bold text-accent">Welcome to StockBot</h2>
      <p class="mt-4 text-lg">Track stocks, view logs, and get insights—all in one place.</p>
      <button class="mt-6 bg-accent text-gray-900 px-6 py-2 rounded-lg hover:bg-blue-400">
        Get Started
      </button>
    </section>

    <!-- Logs Section -->
    <section id="logs" class="py-20 bg-gray-900">
      <div class="container mx-auto">
        <h3 class="text-3xl font-bold text-center text-accent mb-10">Logs</h3>
        <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
          <p class="text-gray-300">Here’s where we’ll display recent logs fetched from the backend.</p>
          <!-- Placeholder for logs -->
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-20">
      <div class="container mx-auto">
        <h3 class="text-3xl font-bold text-center text-accent mb-10">Features</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-gray-800 p-6 rounded-lg hover:shadow-lg">
            <h4 class="text-xl font-bold text-blue-400">Real-Time Tracking</h4>
            <p class="mt-2">Get instant updates on stock prices and alerts.</p>
          </div>
          <div class="bg-gray-800 p-6 rounded-lg hover:shadow-lg">
            <h4 class="text-xl font-bold text-blue-400">Customizable Alerts</h4>
            <p class="mt-2">Set price thresholds and get notified.</p>
          </div>
          <div class="bg-gray-800 p-6 rounded-lg hover:shadow-lg">
            <h4 class="text-xl font-bold text-blue-400">Comprehensive Logs</h4>
            <p class="mt-2">View detailed logs of stock updates and bot activities.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-800 p-4 text-center">
      <p>&copy; 2025 StockBot. All rights reserved.</p>
    </footer>
  </div>
</template>

<style>
body {
  font-family: 'Roboto', sans-serif;
}
</style>
<script>
export default {
  data() {
    return {
      logs: [],
    };
  },
  async created() {
    try {
      const response = await fetch("https://your-app.herokuapp.com/logs");
      const data = await response.json();
      if (data.logs) {
        this.logs = data.logs;
      }
    } catch (error) {
      console.error("Failed to fetch logs:", error);
    }
  },
};
</script>

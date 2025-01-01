<template>
    <div class="logs-viewer">
      <h1>Logs Viewer</h1>
      <button @click="fetchLogs">Refresh Logs</button>
      <pre v-if="logs">{{ logs }}</pre>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    name: "LogsViewer",
    data() {
      return {
        logs: "",
        error: "",
      };
    },
    methods: {
      async fetchLogs() {
        try {
          const response = await axios.get("/logs");
          this.logs = response.data.logs.join("\n");
          this.error = "";
        } catch (err) {
          this.error = "Failed to fetch logs.";
          console.error(err);
        }
      },
    },
    mounted() {
      this.fetchLogs();
    },
  };
  </script>
  
  <style scoped>
  .logs-viewer {
    font-family: Arial, sans-serif;
    margin: 20px;
  }
  button {
    margin-bottom: 10px;
  }
  pre {
    background-color: #f8f9fa;
    padding: 15px;
    border: 1px solid #ddd;
  }
  .error {
    color: red;
  }
  </style>
  
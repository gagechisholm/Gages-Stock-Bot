<template>
  <div id="app">
    <LogsViewer />
  </div>
</template>

<script>
import LogsViewer from "./components/LogsViewer.vue";

export default {
  name: "App",
  components: {
    LogsViewer,
  },
};
</script>

<style>
body {
  margin: 0;
  padding: 0;
}
</style>

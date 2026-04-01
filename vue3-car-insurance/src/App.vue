<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
// 移除全局 Sidebar，由各页面自行控制是否需要侧边栏
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
}

body {
  margin: 0;
  padding: 0;
}
</style>

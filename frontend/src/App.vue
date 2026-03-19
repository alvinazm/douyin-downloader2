<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'

onMounted(() => {
  const footer = document.querySelector('footer')
  if (footer) {
    footer.remove()
  }
})
</script>

<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<style>
:root {
  --primary: #0F172A;
  --primary-light: #1E293B;
  --primary-dark: #020617;
  --accent: #3B82F6;
  --accent-hover: #2563EB;
  --accent-subtle: #DBEAFE;
  
  --neutral-900: #111827;
  --neutral-800: #1F2937;
  --neutral-700: #374151;
  --neutral-600: #4B5563;
  --neutral-500: #6B7280;
  --neutral-400: #9CA3AF;
  --neutral-300: #D1D5DB;
  --neutral-200: #E5E7EB;
  --neutral-100: #F3F4F6;
  --neutral-50: #F9FAFB;
  
  --bg-primary: #FFFFFF;
  --bg-secondary: #F9FAFB;
  --bg-tertiary: #F3F4F6;
  --bg-elevated: #FFFFFF;
  
  --success: #10B981;
  --warning: #F59E0B;
  --error: #EF4444;
  
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  
  --font-display: 'SF Pro Display', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  --font-body: 'SF Pro Text', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
  
  --ease-out: cubic-bezier(0.215, 0.61, 0.355, 1);
  --ease-in-out: cubic-bezier(0.645, 0.045, 0.355, 1);
}

*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-body);
  font-size: 14px;
  line-height: 1.5;
  color: var(--neutral-900);
  background-color: var(--bg-secondary);
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-display);
  font-weight: 600;
  line-height: 1.2;
  color: var(--neutral-900);
  margin: 0;
}

h1 {
  font-size: 28px;
  font-weight: 700;
}

h2 {
  font-size: 20px;
  font-weight: 600;
}

h3 {
  font-size: 18px;
  font-weight: 600;
}

h4 {
  font-size: 16px;
  font-weight: 600;
}

p {
  margin: 0;
}

a {
  color: var(--accent);
  text-decoration: none;
  transition: color 0.15s var(--ease-out);
}

a:hover {
  color: var(--accent-hover);
}

button {
  font-family: var(--font-body);
  cursor: pointer;
  border: none;
  outline: none;
  background: none;
}

input, textarea, select {
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--neutral-900);
}

#app {
  min-height: 100vh;
  background: var(--bg-secondary);
}
</style>

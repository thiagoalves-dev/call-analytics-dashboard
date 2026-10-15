<script setup lang="ts">
withDefaults(defineProps<{ size?: number }>(), { size: 28 });
</script>

<template>
  <svg class="logo" :width="size" :height="size" viewBox="0 0 32 32" aria-hidden="true">
    <defs>
      <linearGradient id="logo-gradient" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="#7c7cf0" />
        <stop offset="1" stop-color="#4f46c8" />
      </linearGradient>
    </defs>
    <rect width="32" height="32" rx="8" fill="url(#logo-gradient)" />
    <rect x="8" y="16" width="3.5" height="8" rx="1.75" fill="#ffffff" fill-opacity="0.65" />
    <rect x="14.25" y="11" width="3.5" height="13" rx="1.75" fill="#ffffff" fill-opacity="0.85" />
    <rect x="20.5" y="7" width="3.5" height="17" rx="1.75" fill="#ffffff" />
  </svg>
</template>

<style scoped>
.logo {
  display: block;
  flex-shrink: 0;
}
</style>

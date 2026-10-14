<script setup lang="ts">
import type { CallStatus } from "../api/types";
import { STATUS_COLORS, STATUS_LABELS } from "../lib/statusColors";

defineProps<{ status: CallStatus }>();
</script>

<template>
  <span class="badge" :style="{ color: STATUS_COLORS[status], borderColor: STATUS_COLORS[status] }">
    {{ STATUS_LABELS[status] }}
  </span>
</template>

<style scoped>
.badge {
  display: inline-block;
  padding: 1px 8px;
  border: 1px solid;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}
</style>

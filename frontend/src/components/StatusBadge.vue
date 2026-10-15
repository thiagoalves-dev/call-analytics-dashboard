<script setup lang="ts">
import type { CallStatus } from "../api/types";
import { STATUS_LABELS } from "../lib/statusColors";

defineProps<{ status: CallStatus }>();
</script>

<template>
  <span class="badge" :class="status">{{ STATUS_LABELS[status] }}</span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 9px 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}
.badge::before {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}
.missed {
  color: var(--missed-ink);
  background: var(--missed-soft);
}
.connected {
  color: var(--connected-ink);
  background: var(--connected-soft);
}
.converted {
  color: var(--converted-ink);
  background: var(--converted-soft);
}
</style>

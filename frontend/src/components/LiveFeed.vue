<script setup lang="ts">
import type { Call } from "../api/types";
import type { StreamState } from "../composables/useLiveCalls";
import { formatCallTime, formatDuration, formatPhone } from "../lib/format";
import StatusBadge from "./StatusBadge.vue";

defineProps<{ calls: Call[]; timezone: string; streamState: StreamState; live: boolean }>();

const STATE_LABELS: Record<StreamState, string> = {
  connecting: "Connecting…",
  live: "Live",
  reconnecting: "Reconnecting…",
};
</script>

<template>
  <section class="panel">
    <header>
      <h2>Recent calls</h2>
      <span v-if="live" class="state" :class="streamState">● {{ STATE_LABELS[streamState] }}</span>
      <span v-else class="state paused">Paused — custom range</span>
    </header>
    <p v-if="calls.length === 0" class="empty">No calls match these filters.</p>
    <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Ended</th>
            <th>Campaign</th>
            <th>Caller</th>
            <th>Duration</th>
            <th>Outcome</th>
          </tr>
        </thead>
        <TransitionGroup tag="tbody" name="arrive">
          <tr v-for="call in calls" :key="call.id">
            <td class="nowrap">{{ formatCallTime(call.ended_at, timezone) }}</td>
            <td>
              {{ call.campaign_name }}
              <small>{{ call.source }}</small>
            </td>
            <td class="nowrap">{{ formatPhone(call.caller_number) }}</td>
            <td>{{ formatDuration(call.duration_seconds) }}</td>
            <td><StatusBadge :status="call.status" /></td>
          </tr>
        </TransitionGroup>
      </table>
    </div>
  </section>
</template>

<style scoped>
header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.state {
  font-size: 13px;
  font-weight: 600;
}
.state.live {
  color: #12a594;
}
.state.connecting,
.state.reconnecting {
  color: #d9822b;
}
.state.paused {
  color: var(--muted);
}
.table-wrapper {
  max-height: 460px;
  overflow: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
th {
  text-align: left;
  color: var(--muted);
  font-weight: 500;
  position: sticky;
  top: 0;
  background: var(--surface);
}
th,
td {
  padding: 8px 6px;
  border-bottom: 1px solid var(--border);
}
small {
  display: block;
  color: var(--muted);
}
.nowrap {
  white-space: nowrap;
}
.empty {
  color: var(--muted);
}
.arrive-enter-active {
  transition: background-color 2s ease;
}
.arrive-enter-from {
  background-color: rgba(18, 165, 148, 0.18);
}
</style>

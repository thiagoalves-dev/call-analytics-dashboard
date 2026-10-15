<script setup lang="ts">
import type { Call } from "../api/types";
import type { StreamState } from "../composables/useLiveCalls";
import { formatCallTime, formatDuration, formatPhone } from "../lib/format";
import StatusBadge from "./StatusBadge.vue";

defineProps<{ calls: Call[]; timezone: string; streamState: StreamState }>();

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
      <span class="state" :class="streamState"><span class="pulse-dot"></span>{{ STATE_LABELS[streamState] }}</span>
    </header>
    <p v-if="calls.length === 0" class="empty">No calls match these filters.</p>
    <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Ended</th>
            <th>Campaign</th>
            <th>Caller</th>
            <th class="numeric">Duration</th>
            <th>Outcome</th>
          </tr>
        </thead>
        <TransitionGroup tag="tbody" name="arrive">
          <tr v-for="call in calls" :key="call.id">
            <td class="time">{{ formatCallTime(call.ended_at, timezone) }}</td>
            <td class="campaign">
              {{ call.campaign_name }}
              <small>{{ call.source }}</small>
            </td>
            <td class="caller">{{ formatPhone(call.caller_number) }}</td>
            <td class="duration numeric">{{ formatDuration(call.duration_seconds) }}</td>
            <td class="outcome"><StatusBadge :status="call.status" /></td>
          </tr>
        </TransitionGroup>
      </table>
    </div>
  </section>
</template>

<style scoped>
.state {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: 999px;
}
.state.live {
  color: var(--converted-ink);
  background: var(--converted-soft);
}
.state.connecting,
.state.reconnecting {
  color: var(--warning);
  background: var(--subtle);
}
.table-wrapper {
  max-height: 460px;
  overflow: auto;
  margin: 0 -20px -20px;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
th {
  text-align: left;
  color: var(--muted);
  font-size: 12px;
  font-weight: 500;
  position: sticky;
  top: 0;
  z-index: 1;
  background: var(--surface);
  box-shadow: inset 0 -1px 0 var(--border);
}
th,
td {
  padding: 10px 12px;
  white-space: nowrap;
}
th:first-child,
td:first-child {
  padding-left: 20px;
}
th:last-child,
td:last-child {
  padding-right: 20px;
}
td {
  border-bottom: 1px solid var(--border);
}
tbody tr:last-child td {
  border-bottom: none;
}
tbody tr {
  transition: background-color 0.15s ease;
}
tbody tr:hover {
  background: var(--subtle);
}
.time,
.caller,
.duration {
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}
.campaign {
  font-weight: 500;
  white-space: normal;
}
small {
  display: block;
  color: var(--muted);
  font-size: 12px;
  font-weight: 400;
}
.numeric {
  text-align: right;
}
.empty {
  color: var(--muted);
  margin: 0;
}
.arrive-enter-active {
  transition: background-color 2.4s ease;
}
.arrive-enter-from {
  background-color: var(--accent-soft);
}
@media (max-width: 640px) {
  .table-wrapper {
    margin: 0 -16px -16px;
  }
  thead {
    display: none;
  }
  tbody tr {
    display: grid;
    grid-template-columns: auto auto minmax(0, 1fr) auto;
    grid-template-areas: "campaign campaign campaign outcome" "time caller duration duration";
    column-gap: 8px;
    row-gap: 6px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
  }
  td,
  td:first-child,
  td:last-child {
    padding: 0;
    border: none;
  }
  .campaign {
    grid-area: campaign;
  }
  .outcome {
    grid-area: outcome;
    justify-self: end;
  }
  .time {
    grid-area: time;
  }
  .caller {
    grid-area: caller;
  }
  .duration {
    grid-area: duration;
    text-align: left;
  }
  .time,
  .caller,
  .duration {
    font-size: 12px;
  }
  .caller::before,
  .duration::before {
    content: "·";
    margin-right: 8px;
  }
}
</style>

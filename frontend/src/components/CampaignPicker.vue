<script setup lang="ts">
import { computed, ref } from "vue";
import type { Campaign } from "../api/types";

const props = defineProps<{ campaigns: Campaign[] }>();
const selectedIds = defineModel<number[]>({ required: true });
const open = ref(false);

const summary = computed(() => {
  if (selectedIds.value.length === 0) return "All campaigns";
  if (selectedIds.value.length === 1) return props.campaigns.find((campaign) => campaign.id === selectedIds.value[0])?.name;
  return `${selectedIds.value.length} campaigns`;
});

function closeWhenFocusLeaves(event: FocusEvent) {
  const picker = event.currentTarget as Element;
  if (!picker.contains(event.relatedTarget as Node)) open.value = false;
}
</script>

<template>
  <div class="picker" @focusout="closeWhenFocusLeaves">
    <button
      type="button"
      class="trigger"
      :class="{ filtered: selectedIds.length > 0 }"
      aria-label="Campaigns"
      :aria-expanded="open"
      @click="open = !open"
    >
      <svg class="icon" viewBox="0 0 16 16" aria-hidden="true">
        <path d="M2.5 4h11M4.5 8h7M6.5 12h3" />
      </svg>
      <span class="summary">{{ summary }}</span>
      <svg class="chevron" :class="{ open }" viewBox="0 0 16 16" aria-hidden="true">
        <path d="M4.5 6.5 8 10l3.5-3.5" />
      </svg>
    </button>
    <div v-if="open" class="menu" tabindex="-1">
      <label v-for="campaign in campaigns" :key="campaign.id">
        <input v-model="selectedIds" type="checkbox" :value="campaign.id" />
        <span>{{ campaign.name }}</span>
        <small>{{ campaign.source }}</small>
      </label>
    </div>
  </div>
</template>

<style scoped>
.picker {
  position: relative;
  min-width: 0;
}
.trigger {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  max-width: 100%;
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 9px;
  padding: 6px 10px;
  min-width: 200px;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.15s ease;
}
.trigger:hover {
  border-color: var(--border-strong);
}
.trigger.filtered {
  border-color: var(--accent);
  background: var(--accent-soft);
  color: var(--accent-ink);
}
.summary {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.icon,
.chevron {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.6;
  stroke-linecap: round;
  stroke-linejoin: round;
  color: var(--muted);
}
.chevron {
  transition: transform 0.15s ease;
}
.chevron.open {
  transform: rotate(180deg);
}
.menu {
  position: absolute;
  z-index: 10;
  top: calc(100% + 6px);
  left: 0;
  width: max-content;
  min-width: 300px;
  max-width: calc(100vw - 32px);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  box-shadow: var(--shadow-raised);
  padding: 6px;
}
label {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 7px 8px;
  border-radius: 6px;
  font-size: 13px;
  color: var(--text);
  cursor: pointer;
}
label:hover {
  background: var(--subtle);
}
input {
  accent-color: var(--accent);
  margin: 0;
}
small {
  color: var(--muted);
  font-size: 12px;
}
</style>

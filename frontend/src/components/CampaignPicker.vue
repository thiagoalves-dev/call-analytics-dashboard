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
    <button type="button" class="trigger" @click="open = !open">{{ summary }} ▾</button>
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
}
.trigger {
  font: inherit;
  color: var(--text);
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 6px 10px;
  min-width: 220px;
  text-align: left;
  cursor: pointer;
}
.menu {
  position: absolute;
  z-index: 10;
  top: calc(100% + 4px);
  left: 0;
  min-width: 320px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  padding: 6px;
}
label {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 6px;
  color: var(--text);
  cursor: pointer;
}
label:hover {
  background: var(--background);
}
small {
  color: var(--muted);
}
</style>

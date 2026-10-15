import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { defaultFilters, type Filters } from "../lib/filters";
import FilterBar from "./FilterBar.vue";

function mountFilterBar(filters: Filters) {
  return mount(FilterBar, { props: { campaigns: [], filters } });
}

const buttonLabelled = (wrapper: ReturnType<typeof mountFilterBar>, label: string) =>
  wrapper.findAll("button").find((button) => button.text() === label)!;

describe("FilterBar", () => {
  it("emits new filters with the outcome added when an outcome is toggled on", async () => {
    const filters = defaultFilters();
    const wrapper = mountFilterBar(filters);

    await buttonLabelled(wrapper, "Converted").trigger("click");

    expect(wrapper.emitted("update:filters")).toEqual([[{ ...filters, statuses: ["converted"] }]]);
    expect(filters.statuses).toEqual([]);
  });

  it("emits new filters with the outcome removed when an active outcome is toggled off", async () => {
    const wrapper = mountFilterBar({ ...defaultFilters(), statuses: ["missed", "converted"] });

    await buttonLabelled(wrapper, "Missed").trigger("click");

    expect(wrapper.emitted("update:filters")?.[0]).toEqual([{ ...defaultFilters(), statuses: ["converted"] }]);
  });

  it("emits new filters for the selected date range", async () => {
    const wrapper = mountFilterBar(defaultFilters());

    await wrapper.get("[aria-label='Last 90 days']").trigger("click");

    expect(wrapper.emitted("update:filters")?.[0]).toEqual([{ ...defaultFilters(), preset: "90d" }]);
  });

  it("emits cleared campaign and outcome filters", async () => {
    const wrapper = mountFilterBar({ preset: "30d", campaignIds: [1], statuses: ["missed"] });

    await buttonLabelled(wrapper, "Clear filters").trigger("click");

    expect(wrapper.emitted("update:filters")?.[0]).toEqual([{ preset: "30d", campaignIds: [], statuses: [] }]);
  });
});

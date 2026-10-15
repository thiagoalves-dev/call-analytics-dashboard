import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { buildConversionRow } from "../test/fixtures";
import KpiCards from "./KpiCards.vue";

describe("KpiCards", () => {
  it("shows placeholders instead of zeros before the first load", () => {
    const wrapper = mount(KpiCards, { props: { rows: null, outcomeFiltered: false } });

    expect(wrapper.findAll(".placeholder")).toHaveLength(4);
    expect(wrapper.findAll("strong").map((value) => value.text())).toEqual(["", "", "", ""]);
  });

  it("shows the totals once rows have loaded", () => {
    const rows = [buildConversionRow({ calls: 10, converted: 3, missed: 1 })];
    const wrapper = mount(KpiCards, { props: { rows, outcomeFiltered: false } });

    expect(wrapper.find(".placeholder").exists()).toBe(false);
    expect(wrapper.findAll("strong").map((value) => value.text())).toEqual(["10", "3", "30%", "10%"]);
  });
});

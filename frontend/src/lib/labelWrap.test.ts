import { describe, expect, it } from "vitest";
import { wrapLabel } from "./labelWrap";

const MAX_LINE_LENGTH = 12;

describe("wrapLabel", () => {
  it("keeps a short label on one line", () => {
    expect(wrapLabel("Google Ads", MAX_LINE_LENGTH)).toEqual(["Google Ads"]);
  });

  it("wraps a long label by words without exceeding the line length", () => {
    const lines = wrapLabel("Spring sale on regional radio", MAX_LINE_LENGTH);

    expect(lines).toEqual(["Spring sale", "on regional", "radio"]);
  });

  it("drops a separator left dangling at a line break", () => {
    expect(wrapLabel("Google Search - HVAC Repair", MAX_LINE_LENGTH)).toEqual(["Google", "Search", "HVAC Repair"]);
  });

  it("keeps a separator in the middle of a line", () => {
    expect(wrapLabel("TV - Ads", MAX_LINE_LENGTH)).toEqual(["TV - Ads"]);
  });

  it("puts a word longer than the line length on a line of its own", () => {
    expect(wrapLabel("Unbelievablylongword now", MAX_LINE_LENGTH)).toEqual(["Unbelievablylongword", "now"]);
  });

  it("collapses repeated whitespace", () => {
    expect(wrapLabel("  Direct   Mail  ", MAX_LINE_LENGTH)).toEqual(["Direct Mail"]);
  });
});

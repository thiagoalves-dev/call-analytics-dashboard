import { describe, expect, it, vi } from "vitest";
import { deferred } from "../test/fixtures";
import { createLatestResponseGuard } from "./latestResponse";

describe("createLatestResponseGuard", () => {
  it("ignores a response that arrives after a newer request was issued", async () => {
    const applyLatest = createLatestResponseGuard();
    const apply = vi.fn();
    const slow = deferred<string>();

    const first = applyLatest(() => slow.promise, apply);
    await applyLatest(() => Promise.resolve("newer"), apply);
    slow.resolve("older");
    await first;

    expect(apply).toHaveBeenCalledOnce();
    expect(apply).toHaveBeenCalledWith("newer");
  });

  it("swallows the failure of a superseded request", async () => {
    const applyLatest = createLatestResponseGuard();
    const slow = deferred<string>();

    const first = applyLatest(() => slow.promise, vi.fn());
    await applyLatest(() => Promise.resolve("newer"), vi.fn());
    slow.reject(new Error("too late"));

    await expect(first).resolves.toBeUndefined();
  });

  it("rethrows the failure of the latest request", async () => {
    const applyLatest = createLatestResponseGuard();

    await expect(applyLatest(() => Promise.reject(new Error("down")), vi.fn())).rejects.toThrow("down");
  });
});

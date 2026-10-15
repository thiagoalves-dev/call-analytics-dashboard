export type ApplyLatest = <T>(request: () => Promise<T>, apply: (response: T) => void) => Promise<void>;

export function createLatestResponseGuard(): ApplyLatest {
  let latestTicket = 0;
  return async function applyLatest(request, apply) {
    const ticket = ++latestTicket;
    const isLatest = () => ticket === latestTicket;
    try {
      const response = await request();
      if (isLatest()) apply(response);
    } catch (failure) {
      if (isLatest()) throw failure;
    }
  };
}

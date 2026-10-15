export class UnauthenticatedError extends Error {}

export class ApiError extends Error {}

export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    ...init,
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...init.headers },
  });
  if (response.status === 401) {
    throw new UnauthenticatedError(await errorMessage(response));
  }
  if (!response.ok) {
    throw new ApiError(await errorMessage(response));
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

async function errorMessage(response: Response): Promise<string> {
  const body = await response.json().catch(() => ({}));
  return typeof body.detail === "string" ? body.detail : response.statusText;
}

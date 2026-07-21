type ApiFailure = {
  requestId: string;
  method: "GET" | "POST";
  path: string;
  status: number;
  durationMs: number;
  error: string;
};

/** Emit one machine-readable API failure without request payloads or secrets. */
export function logApiFailure(failure: ApiFailure): void {
  console.error(JSON.stringify({
    timestamp: new Date().toISOString(),
    level: "error",
    event: "fastapi_request_failed",
    request_id: failure.requestId,
    method: failure.method,
    path: failure.path,
    status: failure.status,
    duration_ms: failure.durationMs,
    error: failure.error,
  }));
}

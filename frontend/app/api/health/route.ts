import { randomUUID } from "node:crypto";

import { getBackendHealth } from "@/lib/api";

export const dynamic = "force-dynamic";

/** Report whether this Next.js process can reach the FastAPI process. */
export async function GET(): Promise<Response> {
  const requestId = randomUUID();
  const headers = {
    "Cache-Control": "no-store",
    "X-Request-ID": requestId,
  };
  try {
    const backend = await getBackendHealth(requestId);
    return Response.json({ status: "ok", backend: backend.status, request_id: requestId }, { headers });
  } catch {
    return Response.json(
      { status: "unavailable", backend: "unavailable", request_id: requestId },
      { status: 503, headers },
    );
  }
}

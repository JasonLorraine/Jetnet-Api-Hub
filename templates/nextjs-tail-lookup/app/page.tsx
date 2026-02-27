"use client";

import { useState } from "react";

interface AircraftCard {
  aircraftId: number;
  regNbr: string;
  serialNbr: string;
  make: string;
  model: string;
  year: number | null;
  ownerCompanyId: number | null;
  operatorCompanyId: number | null;
}

interface CompanyCard {
  companyId: number;
  companyName: string;
  segment: string | null;
  location: string | null;
  primaryPhone: string | null;
}

interface GoldenPathResult {
  aircraft: AircraftCard;
  owner: CompanyCard | null;
  operator: CompanyCard | null;
  utilization: Record<string, unknown> | null;
  _debug: Record<string, unknown>;
}

interface ErrorResult {
  code: string;
  message: string;
  endpoint: string | null;
  rawResponsestatus: string | null;
}

export default function Home() {
  const [tail, setTail] = useState("");
  const [result, setResult] = useState<GoldenPathResult | null>(null);
  const [error, setError] = useState<ErrorResult | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleLookup(e: React.FormEvent) {
    e.preventDefault();
    if (!tail.trim()) return;

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const res = await fetch(`/api/lookup?tail=${encodeURIComponent(tail.trim())}`);
      const data = await res.json();

      if (!res.ok || data.code) {
        setError(data as ErrorResult);
      } else {
        setResult(data as GoldenPathResult);
      }
    } catch {
      setError({ code: "NETWORK_ERROR", message: "Failed to reach the server", endpoint: null, rawResponsestatus: null });
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 600, margin: "0 auto" }}>
      <h1>JETNET Tail Lookup</h1>

      <form onSubmit={handleLookup} style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem" }}>
        <input
          type="text"
          value={tail}
          onChange={(e) => setTail(e.target.value)}
          placeholder="Enter tail number (e.g. N123AB)"
          style={{ flex: 1, padding: "0.5rem", fontSize: "1rem" }}
        />
        <button type="submit" disabled={loading} style={{ padding: "0.5rem 1rem", fontSize: "1rem" }}>
          {loading ? "Looking up..." : "Lookup"}
        </button>
      </form>

      {error && (
        <div style={{ background: "#fee", border: "1px solid #c00", padding: "1rem", borderRadius: 4 }}>
          <strong>{error.code}</strong>: {error.message}
        </div>
      )}

      {result && (
        <div>
          <h2>Aircraft</h2>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <tbody>
              {Object.entries(result.aircraft).map(([key, val]) => (
                <tr key={key} style={{ borderBottom: "1px solid #ddd" }}>
                  <td style={{ padding: "0.4rem", fontWeight: "bold" }}>{key}</td>
                  <td style={{ padding: "0.4rem" }}>{val != null ? String(val) : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {result.owner && (
            <>
              <h2>Owner</h2>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <tbody>
                  {Object.entries(result.owner).map(([key, val]) => (
                    <tr key={key} style={{ borderBottom: "1px solid #ddd" }}>
                      <td style={{ padding: "0.4rem", fontWeight: "bold" }}>{key}</td>
                      <td style={{ padding: "0.4rem" }}>{val != null ? String(val) : "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}

          {result.operator && (
            <>
              <h2>Operator</h2>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <tbody>
                  {Object.entries(result.operator).map(([key, val]) => (
                    <tr key={key} style={{ borderBottom: "1px solid #ddd" }}>
                      <td style={{ padding: "0.4rem", fontWeight: "bold" }}>{key}</td>
                      <td style={{ padding: "0.4rem" }}>{val != null ? String(val) : "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </div>
      )}
    </main>
  );
}

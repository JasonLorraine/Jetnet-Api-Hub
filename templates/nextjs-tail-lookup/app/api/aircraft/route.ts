/**
 * app/api/aircraft/route.ts -- Server route for tail number lookup
 *
 * POST /api/aircraft
 * Body: { tailNumber: string }
 * Returns: GoldenPathResult JSON
 */

import { NextRequest, NextResponse } from 'next/server'
import { getRegNumber } from '../../../lib/jetnet'
import { normalize } from '../../../lib/normalize'

export async function POST(req: NextRequest) {
  let tailNumber: string

  try {
    const body = (await req.json()) as { tailNumber?: string }
    tailNumber = (body.tailNumber ?? '').trim()
  } catch {
    return NextResponse.json({ error: 'Invalid request body' }, { status: 400 })
  }

  if (!tailNumber) {
    return NextResponse.json({ error: 'tailNumber is required' }, { status: 400 })
  }

  try {
    const raw = await getRegNumber(tailNumber)
    const result = normalize(raw)

    if (!raw.aircraftresult || !result.aircraftId) {
      return NextResponse.json(
        { error: `Tail number "${tailNumber}" not found in JETNET` },
        { status: 404 }
      )
    }

    return NextResponse.json(result)
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    console.error('[JETNET] getRegNumber error:', message)
    return NextResponse.json(
      { error: `JETNET lookup failed: ${message}` },
      { status: 500 }
    )
  }
}

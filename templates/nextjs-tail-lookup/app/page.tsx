'use client'

import { useState, FormEvent } from 'react'

interface ContactCard {
  fullName: string
  title: string | null
  email: string | null
  phone: string | null
}

interface CompanyCard {
  name: string | null
  city: string | null
  state: string | null
  country: string | null
  contact: ContactCard | null
}

interface Aircraft {
  tailNumber: string
  make: string
  model: string
  yearMfr: number
  categorySize: string | null
  weightClass: string | null
  usage: string | null
  forSale: boolean
  baseIcao: string | null
  baseAirport: string | null
  owner: CompanyCard | null
  operator: CompanyCard | null
  jetnetPageUrl: string | null
}

export default function Home() {
  const [tailNumber, setTailNumber] = useState('')
  const [result, setResult] = useState<Aircraft | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!tailNumber.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch('/api/aircraft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tailNumber: tailNumber.trim() }),
      })
      const data = await res.json()

      if (!res.ok) {
        setError(data.error ?? 'Lookup failed')
      } else {
        setResult(data as Aircraft)
      }
    } catch {
      setError('Network error -- please try again')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Aircraft Lookup</h1>
        <p className="text-gray-500 mb-8">Enter a tail number to view ownership and contact information.</p>

        <form onSubmit={handleSubmit} className="flex gap-3 mb-8">
          <input
            type="text"
            value={tailNumber}
            onChange={e => setTailNumber(e.target.value.toUpperCase())}
            placeholder="N12345"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-lg font-mono
                       focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading || !tailNumber.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium
                       hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-6">
            {error}
          </div>
        )}

        {result && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="bg-gray-900 text-white px-6 py-4 flex items-center justify-between">
              <div>
                <span className="text-2xl font-mono font-bold">{result.tailNumber}</span>
                <span className="ml-3 text-gray-300">
                  {result.make} {result.model} &bull; {result.yearMfr}
                </span>
              </div>
              {result.forSale && (
                <span className="bg-green-500 text-white text-sm font-medium px-3 py-1 rounded-full">
                  For Sale
                </span>
              )}
            </div>

            <div className="p-6 space-y-6">
              <div>
                <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Aircraft</h2>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  {result.categorySize && <Field label="Category" value={result.categorySize} />}
                  {result.weightClass && <Field label="Weight Class" value={result.weightClass} />}
                  {result.usage && <Field label="Usage" value={result.usage} />}
                  {result.baseIcao && (
                    <Field
                      label="Home Base"
                      value={result.baseAirport ? `${result.baseIcao} -- ${result.baseAirport}` : result.baseIcao}
                    />
                  )}
                </div>
              </div>

              {result.owner && (
                <CompanySection title="Owner" company={result.owner} />
              )}

              {result.operator && result.operator.name !== result.owner?.name && (
                <CompanySection title="Operator" company={result.operator} />
              )}

              {result.jetnetPageUrl && (
                <div className="pt-2 border-t border-gray-100">
                  <a
                    href={result.jetnetPageUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline text-sm"
                  >
                    View full record on JETNET Evolution &rarr;
                  </a>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  )
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-gray-400 text-xs">{label}</dt>
      <dd className="text-gray-900 font-medium">{value}</dd>
    </div>
  )
}

function CompanySection({ title, company }: { title: string; company: CompanyCard }) {
  const location = [company.city, company.state, company.country].filter(Boolean).join(', ')
  return (
    <div>
      <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">{title}</h2>
      <div className="text-sm space-y-1">
        {company.name && <p className="font-semibold text-gray-900">{company.name}</p>}
        {location && <p className="text-gray-500">{location}</p>}
        {company.contact && (
          <div className="mt-2 pt-2 border-t border-gray-100 space-y-1">
            {company.contact.fullName && (
              <p className="text-gray-900">
                {company.contact.fullName}
                {company.contact.title && (
                  <span className="text-gray-400 ml-2">{company.contact.title}</span>
                )}
              </p>
            )}
            {company.contact.phone && (
              <p className="text-gray-600">
                <a href={`tel:${company.contact.phone}`} className="hover:underline">
                  {company.contact.phone}
                </a>
              </p>
            )}
            {company.contact.email && (
              <p className="text-gray-600">
                <a href={`mailto:${company.contact.email}`} className="hover:underline">
                  {company.contact.email}
                </a>
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authorsApi } from '../api/endpoints'
import { useDebouncedValue } from '../lib/useDebouncedValue'

export function HomePage() {
  const [search, setSearch] = useState('')
  const navigate = useNavigate()
  const debouncedSearch = useDebouncedValue(search)

  const { data } = useQuery({
    queryKey: ['home-authors', debouncedSearch],
    queryFn: ({ signal }) => authorsApi.list({ q: debouncedSearch, limit: 6 }, signal),
    enabled: debouncedSearch.trim().length >= 2,
  })

  const suggestions = data ?? []

  return (
    <div className="flex min-h-[75vh] flex-col items-center justify-center">
      <div className="w-full max-w-2xl text-center">
        <h1 className="font-display text-5xl font-extrabold tracking-tight text-slate-900 sm:text-6xl">
          SinergIA
        </h1>
        <p className="mt-4 text-base text-slate-600">
          Busca autores, consulta sus publicaciones, filtra por años y exporta los resultados.
        </p>

        <form
          className="mt-8 flex flex-col gap-2.5 sm:flex-row"
          onSubmit={(event) => {
            event.preventDefault()
            navigate(`/authors?q=${encodeURIComponent(search)}`)
          }}
        >
          <input
            className="input text-base py-3 px-4 shadow-sm"
            placeholder="Buscar un investigador por nombre u ORCID"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <button type="submit" className="btn-primary sm:w-auto px-6 py-3 text-base shadow-sm">
            Buscar
          </button>
        </form>

        {suggestions.length > 0 && (
          <ul className="card mt-4 divide-y divide-slate-100 text-left shadow-md">
            {suggestions.map((author) => (
              <li key={author.id}>
                <Link
                  to={`/authors/${encodeURIComponent(author.id)}`}
                  className="flex items-center justify-between px-4 py-3.5 transition hover:bg-slate-50"
                >
                  <span className="text-sm font-medium text-slate-800">{author.display_name}</span>
                  <span className="text-xs text-slate-500">{author.orcid ?? '—'}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}


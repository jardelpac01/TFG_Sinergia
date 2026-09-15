import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { authorsApi } from '../api/endpoints'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { EmptyState, ErrorState, LoadingState } from '../components/States'
import { useDebouncedValue } from '../lib/useDebouncedValue'
import { downloadCsv } from '../lib/csv'

const PAGE_SIZE = 9

export function AuthorsPage() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const debouncedSearch = useDebouncedValue(search)

  const { data, isPending, isError, error } = useQuery({
    queryKey: ['authors', debouncedSearch, page],
    queryFn: ({ signal }) =>
      authorsApi.list({ q: debouncedSearch, page, page_size: PAGE_SIZE }, signal),
  })

  const authors = data?.items ?? []
  const total = data?.total ?? 0

  function handleSearchChange(value: string) {
    setSearch(value)
    setPage(1)
  }

  function handleExport() {
    downloadCsv('autores.csv', authors, [
      { header: 'ID', value: (author) => author.id },
      { header: 'Nombre', value: (author) => author.display_name },
      { header: 'ORCID', value: (author) => author.orcid },
    ])
  }

  return (
    <div>
      <PageHeader
        title="Autores"
        subtitle="Busca investigadores por nombre u ORCID"
        titleClassName="text-4xl font-bold tracking-tight text-slate-900"
        actions={
          <button
            type="button"
            className="btn-secondary"
            onClick={handleExport}
            disabled={authors.length === 0}
          >
            Exportar CSV
          </button>
        }
      />

      <div className="card mb-6 p-4">
        <label className="label" htmlFor="author-search">
          Búsqueda
        </label>
        <input
          id="author-search"
          className="input"
          placeholder="Ej. García, 0000-0002-…"
          value={search}
          onChange={(event) => handleSearchChange(event.target.value)}
        />
      </div>

      {isPending ? (
        <div className="card">
          <LoadingState />
        </div>
      ) : isError ? (
        <div className="card">
          <ErrorState title="No se pudieron cargar los autores" description={error.message} />
        </div>
      ) : authors.length === 0 ? (
        <div className="card">
          <EmptyState
            title="Sin resultados"
            description="Prueba con otro nombre o revisa que la base de datos tenga autores cargados."
          />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {authors.map((author) => (
              <Link
                key={author.id}
                to={`/authors/${encodeURIComponent(author.id)}`}
                className="card flex flex-col justify-between p-5 transition-all hover:-translate-y-0.5 hover:shadow-md"
              >
                <div>
                  <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-full bg-brand-50 text-brand-700">
                    <svg
                      className="h-6 w-6"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                      />
                    </svg>
                  </div>
                  <h2 className="font-display text-lg font-semibold text-slate-900">
                    {author.display_name}
                  </h2>
                  <p className="mt-1 text-sm text-slate-500">{author.orcid ?? 'Sin ORCID'}</p>
                </div>
              </Link>
            ))}
          </div>

          <div className="mt-6">
            <Pagination
              page={page}
              pageSize={PAGE_SIZE}
              totalItems={total}
              onPageChange={setPage}
            />
          </div>
        </>
      )}
    </div>
  )
}

import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { institutionsApi } from '../api/endpoints'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { EmptyState, ErrorState, LoadingState } from '../components/States'
import { useDebouncedValue } from '../lib/useDebouncedValue'
import { downloadCsv } from '../lib/csv'

const PAGE_SIZE = 18

export function InstitutionsPage() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const debouncedSearch = useDebouncedValue(search)

  const { data, isPending, isError, error } = useQuery({
    queryKey: ['institutions', debouncedSearch, page],
    queryFn: ({ signal }) =>
      institutionsApi.list({ q: debouncedSearch, page, page_size: PAGE_SIZE }, signal),
  })

  const institutions = data?.items ?? []
  const total = data?.total ?? 0

  function handleSearchChange(value: string) {
    setSearch(value)
    setPage(1)
  }

  function handleExport() {
    downloadCsv('instituciones.csv', institutions, [
      { header: 'ID', value: (item) => item.id },
      { header: 'Nombre', value: (item) => item.name },
      { header: 'País', value: (item) => item.country_code },
      { header: 'Ciudad', value: (item) => item.city },
      { header: 'Tipo', value: (item) => item.type },
      { header: 'ROR', value: (item) => item.ror },
    ])
  }

  return (
    <div>
      <PageHeader
        title="Instituciones"
        subtitle="Busca por nombre o código de país"
        titleClassName="text-4xl font-bold tracking-tight text-slate-900"
        actions={
          <button
            type="button"
            className="btn-secondary"
            onClick={handleExport}
            disabled={institutions.length === 0}
          >
            Exportar CSV
          </button>
        }
      />

      <div className="card mb-6 p-4">
        <label className="label" htmlFor="institution-search">
          Búsqueda
        </label>
        <input
          id="institution-search"
          className="input"
          placeholder="Ej. Universidad, ES"
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
          <ErrorState title="No se pudieron cargar las instituciones" description={error.message} />
        </div>
      ) : institutions.length === 0 ? (
        <div className="card">
          <EmptyState title="Sin resultados" description="Prueba con otro nombre o código de país." />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {institutions.map((institution) => (
              <Link
                key={institution.id}
                to={`/institutions/${encodeURIComponent(institution.id)}`}
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
                        d="M3 21h18M5 21V7l7-4 7 4v14M9 9h1m-1 4h1m4-4h1m-1 4h1M9 21v-4a3 3 0 016 0v4"
                      />
                    </svg>
                  </div>
                  <h2 className="font-display text-lg font-semibold text-slate-900">
                    {institution.name}
                  </h2>
                  <p className="mt-1 text-sm text-slate-500">
                    {[institution.city, institution.country_code].filter(Boolean).join(', ') ||
                      'Ubicación desconocida'}
                  </p>
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


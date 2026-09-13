import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { authorsApi } from '../api/endpoints'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { EmptyState, ErrorState, LoadingState } from '../components/States'
import { useDebouncedValue } from '../lib/useDebouncedValue'
import { downloadCsv } from '../lib/csv'
import { paginate } from '../lib/pagination'

const PAGE_SIZE = 10

export function AuthorsPage() {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const debouncedSearch = useDebouncedValue(search)

  const { data, isPending, isError, error } = useQuery({
    queryKey: ['authors', debouncedSearch],
    queryFn: ({ signal }) => authorsApi.list({ q: debouncedSearch, limit: 200 }, signal),
  })

  const authors = useMemo(() => data ?? [], [data])
  const pageItems = useMemo(() => paginate(authors, page, PAGE_SIZE), [authors, page])

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

      <div className="card mb-4 p-4">
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

      <div className="card overflow-hidden">
        {isPending ? (
          <LoadingState />
        ) : isError ? (
          <ErrorState title="No se pudieron cargar los autores" description={error.message} />
        ) : authors.length === 0 ? (
          <EmptyState
            title="Sin resultados"
            description="Prueba con otro nombre o revisa que la base de datos tenga autores cargados."
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="px-4 py-3 font-medium">Nombre</th>
                    <th className="px-4 py-3 font-medium">ORCID</th>
                    <th className="px-4 py-3 font-medium" />
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {pageItems.map((author) => (
                    <tr key={author.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium text-slate-800">
                        {author.display_name}
                      </td>
                      <td className="px-4 py-3 text-slate-500">{author.orcid ?? '—'}</td>
                      <td className="px-4 py-3 text-right">
                        <Link
                          to={`/authors/${encodeURIComponent(author.id)}`}
                          className="text-sm font-medium text-brand-600 hover:text-brand-700"
                        >
                          Ver ficha
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination
              page={page}
              pageSize={PAGE_SIZE}
              totalItems={authors.length}
              onPageChange={setPage}
            />
          </>
        )}
      </div>
    </div>
  )
}

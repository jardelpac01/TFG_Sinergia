import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { worksApi } from '../api/endpoints'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { EmptyState, ErrorState, LoadingState } from '../components/States'
import { useDebouncedValue } from '../lib/useDebouncedValue'
import { downloadCsv } from '../lib/csv'
import { paginate } from '../lib/pagination'

const PAGE_SIZE = 10

export function WorksPage() {
  const [search, setSearch] = useState('')
  const [fromMonth, setFromMonth] = useState('')
  const [toMonth, setToMonth] = useState('')
  const [page, setPage] = useState(1)
  const debouncedSearch = useDebouncedValue(search)

  const { data, isPending, isError, error } = useQuery({
    queryKey: ['works', debouncedSearch],
    queryFn: ({ signal }) => worksApi.list({ q: debouncedSearch, limit: 200 }, signal),
  })

  const works = useMemo(() => {
    const fromYear = fromMonth ? Number(fromMonth.slice(0, 4)) : null
    const toYear = toMonth ? Number(toMonth.slice(0, 4)) : null

    return (data ?? []).filter((work) => {
      const workMonth = work.publication_date?.slice(0, 7) ?? null

      if (workMonth) {
        if (fromMonth && workMonth < fromMonth) return false
        if (toMonth && workMonth > toMonth) return false
        return true
      }

      // Sin fecha exacta: usar el año como aproximación.
      if (work.publication_year === null) return !fromMonth && !toMonth
      if (fromYear !== null && work.publication_year < fromYear) return false
      if (toYear !== null && work.publication_year > toYear) return false
      return true
    })
  }, [data, fromMonth, toMonth])

  const pageItems = useMemo(() => paginate(works, page, PAGE_SIZE), [works, page])

  function updateFilter(setter: (value: string) => void, value: string) {
    setter(value)
    setPage(1)
  }

  function handleExport() {
    downloadCsv('publicaciones.csv', works, [
      { header: 'ID', value: (work) => work.id },
      { header: 'Título', value: (work) => work.title },
      { header: 'Año', value: (work) => work.publication_year },
      { header: 'Fecha', value: (work) => work.publication_date },
      { header: 'Tipo', value: (work) => work.type },
      { header: 'DOI', value: (work) => work.doi },
      { header: 'Citas', value: (work) => work.cited_by_count },
      { header: 'Acceso abierto', value: (work) => (work.is_oa ? 'Sí' : 'No') },
    ])
  }

  return (
    <div>
      <PageHeader
        title="Publicaciones"
        titleClassName="text-4xl font-bold tracking-tight text-slate-900"
        actions={
          <button
            type="button"
            className="btn-secondary"
            onClick={handleExport}
            disabled={works.length === 0}
          >
            Exportar CSV
          </button>
        }
      />

      <div className="card mb-4 grid gap-4 p-4 sm:grid-cols-4">
        <div className="sm:col-span-2">
          <label className="label" htmlFor="work-search">
            Búsqueda
          </label>
          <div className="relative">
            <svg
              className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
              />
            </svg>
            <input
              id="work-search"
              className="input pl-10"
              placeholder="Título o DOI"
              value={search}
              onChange={(event) => updateFilter(setSearch, event.target.value)}
            />
          </div>
        </div>
        <div>
          <label className="label" htmlFor="works-from">
            Fecha desde
          </label>
          <input
            id="works-from"
            type="month"
            className="input"
            value={fromMonth}
            onChange={(event) => updateFilter(setFromMonth, event.target.value)}
          />
        </div>
        <div>
          <label className="label" htmlFor="works-to">
            Fecha hasta
          </label>
          <input
            id="works-to"
            type="month"
            className="input"
            value={toMonth}
            onChange={(event) => updateFilter(setToMonth, event.target.value)}
          />
        </div>
      </div>

      <div className="card overflow-hidden">
        {isPending ? (
          <LoadingState />
        ) : isError ? (
          <ErrorState title="No se pudieron cargar las publicaciones" description={error.message} />
        ) : works.length === 0 ? (
          <EmptyState title="Sin resultados" description="Ajusta la búsqueda o el rango de fechas." />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="px-4 py-3 font-medium">Título</th>
                    <th className="px-4 py-3 font-medium">Año</th>
                    <th className="px-4 py-3 font-medium">Citas</th>
                    <th className="px-4 py-3 font-medium">DOI</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {pageItems.map((work) => (
                    <tr key={work.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3">
                        <Link
                          to={`/works/${encodeURIComponent(work.id)}`}
                          className="font-medium text-brand-600 hover:text-brand-700"
                        >
                          {work.title}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-slate-600">{work.publication_year ?? '—'}</td>
                      <td className="px-4 py-3 text-slate-600">{work.cited_by_count}</td>
                      <td className="px-4 py-3 text-slate-500">{work.doi ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination
              page={page}
              pageSize={PAGE_SIZE}
              totalItems={works.length}
              onPageChange={setPage}
            />
          </>
        )}
      </div>
    </div>
  )
}

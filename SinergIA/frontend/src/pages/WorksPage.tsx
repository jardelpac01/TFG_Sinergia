import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { worksApi } from '../api/endpoints'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { EmptyState, ErrorState, LoadingState } from '../components/States'
import { useDebouncedValue } from '../lib/useDebouncedValue'
import { downloadBlob } from '../lib/csv'

const PAGE_SIZE = 10

export function WorksPage() {
  const [search, setSearch] = useState('')
  const [fromMonth, setFromMonth] = useState('')
  const [toMonth, setToMonth] = useState('')
  const [page, setPage] = useState(1)
  const [isExporting, setIsExporting] = useState(false)
  const [exportError, setExportError] = useState<string | null>(null)
  const debouncedSearch = useDebouncedValue(search)

  const { data, isPending, isError, error } = useQuery({
    queryKey: ['works', debouncedSearch, fromMonth, toMonth, page],
    queryFn: ({ signal }) =>
      worksApi.list(
        {
          q: debouncedSearch,
          from_month: fromMonth,
          to_month: toMonth,
          page,
          page_size: PAGE_SIZE,
        },
        signal,
      ),
  })

  const pageItems = data?.items ?? []
  const total = data?.total ?? 0

  function updateFilter(setter: (value: string) => void, value: string) {
    setter(value)
    setPage(1)
  }

  async function handleExport() {
    setIsExporting(true)
    setExportError(null)
    try {
      const blob = await worksApi.export({
        q: debouncedSearch,
        from_month: fromMonth,
        to_month: toMonth,
      })
      downloadBlob('publicaciones.csv', blob)
    } catch (exportFailure) {
      setExportError(
        exportFailure instanceof Error
          ? exportFailure.message
          : 'No se pudieron exportar las publicaciones.',
      )
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div>
      <PageHeader
        title="Publicaciones"
        titleClassName="text-4xl font-bold tracking-tight text-slate-900"
        actions={
          <button
            type="button"
            className="btn-primary"
            onClick={handleExport}
            disabled={isExporting || total === 0}
          >
            {isExporting ? 'Exportando…' : 'Exportar'}
          </button>
        }
      />

      {exportError && (
        <div className="mb-4">
          <ErrorState title="No se pudieron exportar las publicaciones" description={exportError} />
        </div>
      )}

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
            max={toMonth || undefined}
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
            min={fromMonth || undefined}
            onChange={(event) => updateFilter(setToMonth, event.target.value)}
          />
        </div>
      </div>

      <div className="card overflow-hidden">
        {isPending ? (
          <LoadingState />
        ) : isError ? (
          <ErrorState title="No se pudieron cargar las publicaciones" description={error.message} />
        ) : pageItems.length === 0 ? (
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
                        {work.versions.length > 1 && (
                          <details className="mt-2 text-xs text-slate-500">
                            <summary className="cursor-pointer text-brand-600 hover:text-brand-700">
                              {work.versions.length} versiones/artefactos asociados
                            </summary>
                            <ul className="mt-2 space-y-1">
                              {work.versions.map((version) => (
                                <li key={version.id}>
                                  <Link
                                    to={`/works/${encodeURIComponent(version.id)}`}
                                    className="text-brand-600 hover:text-brand-700"
                                  >
                                    {version.id}
                                  </Link>
                                  {version.doi ? ` · ${version.doi}` : ''}
                                </li>
                              ))}
                            </ul>
                          </details>
                        )}
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
              totalItems={total}
              onPageChange={setPage}
            />
          </>
        )}
      </div>
    </div>
  )
}

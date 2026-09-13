import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { authorsApi } from '../api/endpoints'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { EmptyState, ErrorState, LoadingState } from '../components/States'
import { downloadCsv } from '../lib/csv'
import { paginate } from '../lib/pagination'

const PAGE_SIZE = 10

export function AuthorDetailPage() {
  const { authorId = '' } = useParams()
  const [fromYear, setFromYear] = useState('')
  const [toYear, setToYear] = useState('')
  const [page, setPage] = useState(1)

  const authorQuery = useQuery({
    queryKey: ['author', authorId],
    queryFn: ({ signal }) => authorsApi.get(authorId, signal),
    enabled: Boolean(authorId),
  })

  const worksQuery = useQuery({
    queryKey: ['author-works', authorId],
    queryFn: ({ signal }) => authorsApi.works(authorId, signal),
    enabled: Boolean(authorId),
  })

  const networkQuery = useQuery({
    queryKey: ['author-network', authorId],
    queryFn: ({ signal }) => authorsApi.network(authorId, signal),
    enabled: Boolean(authorId),
  })

  const filteredWorks = useMemo(() => {
    const works = worksQuery.data ?? []
    const from = fromYear ? Number(fromYear) : null
    const to = toYear ? Number(toYear) : null

    return works.filter((work) => {
      if (work.publication_year === null) return from === null && to === null
      if (from !== null && work.publication_year < from) return false
      if (to !== null && work.publication_year > to) return false
      return true
    })
  }, [worksQuery.data, fromYear, toYear])

  const pageItems = useMemo(() => paginate(filteredWorks, page, PAGE_SIZE), [filteredWorks, page])

  function updateFilter(setter: (value: string) => void, value: string) {
    setter(value)
    setPage(1)
  }

  function handleExport() {
    const author = authorQuery.data
    const range = [fromYear || 'inicio', toYear || 'actual'].join('-')
    downloadCsv(`trabajos-${author?.display_name ?? authorId}-${range}.csv`, filteredWorks, [
      { header: 'ID', value: (work) => work.id },
      { header: 'Título', value: (work) => work.title },
      { header: 'Año', value: (work) => work.publication_year },
      { header: 'Fecha', value: (work) => work.publication_date },
      { header: 'Tipo', value: (work) => work.type },
      { header: 'DOI', value: (work) => work.doi },
      { header: 'Citas', value: (work) => work.cited_by_count },
      { header: 'Acceso abierto', value: (work) => (work.is_oa ? 'Sí' : 'No') },
      { header: 'Estado OA', value: (work) => work.oa_status },
      { header: 'Fuente', value: (work) => work.source?.display_name ?? work.source_id },
      { header: 'Temas', value: (work) => work.topics.map((t) => t.display_name).join(' | ') },
      { header: 'Coautores', value: (work) => work.authors.map((a) => a.display_name).join(' | ') },
    ])
  }

  if (authorQuery.isPending) return <LoadingState label="Cargando autor…" />
  if (authorQuery.isError) {
    return (
      <ErrorState title="No se pudo cargar el autor" description={authorQuery.error.message} />
    )
  }

  const author = authorQuery.data
  const totalCitations = filteredWorks.reduce((sum, work) => sum + work.cited_by_count, 0)
  const openAccessCount = filteredWorks.filter((work) => work.is_oa).length

  return (
    <div>
      <PageHeader
        title={author.display_name}
        subtitle={author.orcid ? `ORCID: ${author.orcid}` : 'Sin ORCID registrado'}
        actions={
          <button
            type="button"
            className="btn-primary"
            onClick={handleExport}
            disabled={filteredWorks.length === 0}
          >
            Exportar selección
          </button>
        }
      />

      <div className="mb-5 grid gap-3 sm:grid-cols-3">
        <StatCard label="Publicaciones" value={filteredWorks.length} />
        <StatCard label="Citas acumuladas" value={totalCitations} />
        <StatCard label="Acceso abierto" value={openAccessCount} />
      </div>

      <div className="card mb-4 grid gap-4 p-4 sm:grid-cols-2">
        <div>
          <label className="label" htmlFor="from-year">
            Año desde
          </label>
          <input
            id="from-year"
            type="number"
            inputMode="numeric"
            className="input"
            placeholder="2018"
            value={fromYear}
            onChange={(event) => updateFilter(setFromYear, event.target.value)}
          />
        </div>
        <div>
          <label className="label" htmlFor="to-year">
            Año hasta
          </label>
          <input
            id="to-year"
            type="number"
            inputMode="numeric"
            className="input"
            placeholder="2025"
            value={toYear}
            onChange={(event) => updateFilter(setToYear, event.target.value)}
          />
        </div>
      </div>

      <section className="card mb-6 overflow-hidden">
        <h2 className="border-b border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700">
          Publicaciones
        </h2>
        {worksQuery.isPending ? (
          <LoadingState />
        ) : worksQuery.isError ? (
          <ErrorState
            title="No se pudieron cargar las publicaciones"
            description={worksQuery.error.message}
          />
        ) : filteredWorks.length === 0 ? (
          <EmptyState
            title="Sin publicaciones en ese rango"
            description="Ajusta los años o limpia los filtros."
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="px-4 py-3 font-medium">Título</th>
                    <th className="px-4 py-3 font-medium">Año</th>
                    <th className="px-4 py-3 font-medium">Citas</th>
                    <th className="px-4 py-3 font-medium">Tipo</th>
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
                      <td className="px-4 py-3 text-slate-600">{work.type ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination
              page={page}
              pageSize={PAGE_SIZE}
              totalItems={filteredWorks.length}
              onPageChange={setPage}
            />
          </>
        )}
      </section>

      <section className="card overflow-hidden">
        <h2 className="border-b border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700">
          Red de colaboración
        </h2>
        {networkQuery.isPending ? (
          <LoadingState />
        ) : networkQuery.isError ? (
          <ErrorState
            title="No se pudo cargar la red"
            description={networkQuery.error.message}
          />
        ) : (networkQuery.data?.coauthors.length ?? 0) === 0 ? (
          <EmptyState title="Sin coautores registrados" />
        ) : (
          <ul className="divide-y divide-slate-100">
            {networkQuery.data?.coauthors.map((coauthor) => (
              <li key={coauthor.id} className="flex items-center justify-between px-4 py-3">
                <Link
                  to={`/authors/${encodeURIComponent(coauthor.id)}`}
                  className="text-sm font-medium text-brand-600 hover:text-brand-700"
                >
                  {coauthor.display_name}
                </Link>
                <span className="badge">{coauthor.shared_works_count} trabajos en común</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="card p-4">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-slate-900">{value}</p>
    </div>
  )
}

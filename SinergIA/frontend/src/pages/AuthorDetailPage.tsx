import { useQuery } from '@tanstack/react-query'
import { useEffect, useMemo, useRef, useState } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { CircleMarker, MapContainer, Popup, TileLayer } from 'react-leaflet'
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
  const leftColumnRef = useRef<HTMLDivElement>(null)
  const [panelHeight, setPanelHeight] = useState<number>()

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

  const cityPoints = useMemo(() => {
    const cities = networkQuery.data?.city_collaborations ?? []
    const maxAuthors = Math.max(1, ...cities.map((city) => city.authors_count))
    return cities.map((city) => ({
      lat: city.geo_lat,
      lon: city.geo_lon,
      count: city.authors_count,
      name: city.city ?? 'Desconocida',
      country: city.country_code,
      // Radius scales between 6px and 22px depending on how many authors were
      // collaborated with in that city, relative to the busiest city.
      radius: 6 + (city.authors_count / maxAuthors) * 16,
    }))
  }, [networkQuery.data])

  const worksByYear = networkQuery.data?.works_by_year ?? []

  useEffect(() => {
    const element = leftColumnRef.current
    if (!element) return

    const updateHeight = () => setPanelHeight(element.offsetHeight)
    updateHeight()

    const observer = new ResizeObserver(updateHeight)
    observer.observe(element)
    return () => observer.disconnect()
  }, [filteredWorks, worksByYear, cityPoints])

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

  return (
    <div>
      <PageHeader
        title={author.display_name}
        subtitle={author.orcid ? `ORCID: ${author.orcid}` : 'Sin ORCID registrado'}
        titleClassName="text-4xl font-bold tracking-tight text-slate-900"
        actions={
          <button
            type="button"
            className="btn-primary"
            onClick={handleExport}
            disabled={filteredWorks.length === 0}
          >
            Exportar
          </button>
        }
      />

      <div className="card mb-6 grid gap-4 p-4 sm:grid-cols-2">
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

      <div className="grid grid-cols-1 items-start gap-6 xl:grid-cols-4">
        <div ref={leftColumnRef} className="space-y-6 xl:col-span-3">
          <section className="card overflow-hidden">
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
                          <td className="px-4 py-3 text-slate-600">
                            {work.publication_year ?? '—'}
                          </td>
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

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <section className="card overflow-hidden">
              <h2 className="border-b border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700">
                Red de autores
              </h2>
              {networkQuery.isPending ? (
                <LoadingState />
              ) : networkQuery.isError ? (
                <ErrorState
                  title="No se pudo cargar el mapa"
                  description={networkQuery.error.message}
                />
              ) : cityPoints.length === 0 ? (
                <EmptyState title="Sin colaboraciones geolocalizadas" />
              ) : (
                <div className="h-72">
                  <MapContainer
                    center={[cityPoints[0].lat, cityPoints[0].lon]}
                    zoom={2}
                    scrollWheelZoom={false}
                    className="h-full w-full"
                  >
                    <TileLayer
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    {cityPoints.map((point) => (
                      <CircleMarker
                        key={`${point.lat}-${point.lon}`}
                        center={[point.lat, point.lon]}
                        radius={point.radius}
                        pathOptions={{
                          color: '#3b82f6',
                          fillColor: '#3b82f6',
                          fillOpacity: 0.6,
                          weight: 1,
                        }}
                      >
                        <Popup>
                          <span className="font-semibold">
                            {point.name}
                            {point.country ? `, ${point.country}` : ''}
                          </span>
                          <br />
                          {point.count} autores colaboradores
                        </Popup>
                      </CircleMarker>
                    ))}
                  </MapContainer>
                </div>
              )}
            </section>

            <section className="card overflow-hidden">
              <h2 className="border-b border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700">
                Publicaciones por año
              </h2>
              {networkQuery.isPending ? (
                <LoadingState />
              ) : networkQuery.isError ? (
                <ErrorState
                  title="No se pudo cargar el gráfico"
                  description={networkQuery.error.message}
                />
              ) : worksByYear.length === 0 ? (
                <EmptyState title="Sin datos suficientes" />
              ) : (
                <div className="h-72 p-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={worksByYear} margin={{ top: 10, right: 10, bottom: 0, left: -10 }}>
                      <CartesianGrid stroke="#e2e8f0" vertical={false} />
                      <XAxis dataKey="year" tick={{ fontSize: 11, fill: '#64748b' }} />
                      <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#64748b' }} />
                      <Tooltip
                        cursor={{ fill: '#f1f5f9' }}
                        formatter={(value: number) => [value, 'Publicaciones']}
                      />
                      <Bar dataKey="works_count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </section>
          </div>
        </div>

        <div className="min-h-0 xl:col-span-1" style={panelHeight ? { height: panelHeight } : undefined}>
          <section className="card flex h-full min-h-0 flex-col overflow-hidden">
            <h2 className="border-b border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700">
              Autores colaboradores
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
              <ul className="min-h-0 flex-1 divide-y divide-slate-100 overflow-y-auto">
                {networkQuery.data?.coauthors.map((coauthor) => (
                  <li key={coauthor.id} className="px-4 py-3">
                    <Link
                      to={`/authors/${encodeURIComponent(coauthor.id)}`}
                      className="block text-sm font-medium text-brand-600 hover:text-brand-700"
                    >
                      {coauthor.display_name}
                    </Link>
                    <span className="badge mt-1 inline-block">
                      {coauthor.shared_works_count} trabajos en común
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </div>
    </div>
  )
}

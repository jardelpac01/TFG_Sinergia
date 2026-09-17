import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { worksApi } from '../api/endpoints'
import { PageHeader } from '../components/PageHeader'
import { EmptyState, ErrorState, LoadingState } from '../components/States'

export function WorkDetailPage() {
  const { workId = '' } = useParams()

  const { data, isPending, isError, error } = useQuery({
    queryKey: ['work', workId],
    queryFn: ({ signal }) => worksApi.get(workId, signal),
    enabled: Boolean(workId),
  })

  if (isPending) return <LoadingState label="Cargando publicación…" />
  if (isError) {
    return <ErrorState title="No se pudo cargar la publicación" description={error.message} />
  }

  return (
    <div>
      <PageHeader
        title={data.title}
        subtitle={[data.publication_year, data.type].filter(Boolean).join(' · ') || undefined}
      />

      <div className="grid gap-4 lg:grid-cols-3">
        <section className="card p-4 lg:col-span-2">
          <h2 className="mb-3 text-sm font-semibold text-slate-700">Detalles</h2>
          <dl className="grid gap-3 sm:grid-cols-2">
            <Detail label="DOI" value={data.doi} />
            <Detail label="Fecha de publicación" value={data.publication_date} />
            <Detail label="Idioma" value={data.language} />
            <Detail label="Citas" value={String(data.cited_by_count)} />
            <Detail label="Acceso abierto" value={data.is_oa ? `Sí (${data.oa_status ?? '—'})` : 'No'} />
            <Detail label="Retractada" value={data.is_retracted ? 'Sí' : 'No'} />
          </dl>

          {data.topics.length > 0 && (
            <div className="mt-4">
              <p className="label">Temas</p>
              <div className="flex flex-wrap gap-2">
                {data.topics.map((topic) => (
                  <span key={topic.id} className="badge">
                    {topic.display_name}
                  </span>
                ))}
              </div>
            </div>
          )}
        </section>

        <section className="card overflow-hidden">
          <h2 className="border-b border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700">
            Investigadores
          </h2>
          {data.authors.length === 0 ? (
            <EmptyState title="Sin investigadores registrados" />
          ) : (
            <ul className="divide-y divide-slate-100">
              {data.authors.map((author) => (
                <li key={author.id} className="px-4 py-3">
                  <Link
                    to={`/authors/${encodeURIComponent(author.id)}`}
                    className="text-sm font-medium text-brand-600 hover:text-brand-700"
                  >
                    {author.display_name}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  )
}

function Detail({ label, value }: { label: string; value: string | null }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-slate-500">{label}</dt>
      <dd className="mt-0.5 text-sm text-slate-800">{value ?? '—'}</dd>
    </div>
  )
}

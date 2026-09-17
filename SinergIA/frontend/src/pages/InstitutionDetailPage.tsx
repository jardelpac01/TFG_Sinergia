import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { institutionsApi } from '../api/endpoints'
import { PageHeader } from '../components/PageHeader'
import { EmptyState, ErrorState, LoadingState } from '../components/States'

export function InstitutionDetailPage() {
  const { institutionId = '' } = useParams()

  const institutionQuery = useQuery({
    queryKey: ['institution', institutionId],
    queryFn: ({ signal }) => institutionsApi.get(institutionId, signal),
    enabled: Boolean(institutionId),
  })

  const authorsQuery = useQuery({
    queryKey: ['institution-authors', institutionId],
    queryFn: ({ signal }) => institutionsApi.authors(institutionId, signal),
    enabled: Boolean(institutionId),
  })

  if (institutionQuery.isPending) return <LoadingState label="Cargando institución…" />
  if (institutionQuery.isError) {
    return (
      <ErrorState
        title="No se pudo cargar la institución"
        description={institutionQuery.error.message}
      />
    )
  }

  const institution = institutionQuery.data

  return (
    <div>
      <PageHeader
        title={institution.name}
        subtitle={[institution.city, institution.country_code].filter(Boolean).join(', ') || undefined}
      />

      <div className="grid gap-4 lg:grid-cols-3">
        <section className="card p-4">
          <h2 className="mb-3 text-sm font-semibold text-slate-700">Datos</h2>
          <dl className="space-y-3">
            <Detail label="Tipo" value={institution.type} />
            <Detail label="ROR" value={institution.ror} />
            <Detail label="País" value={institution.country_code} />
          </dl>
        </section>

        <section className="card overflow-hidden lg:col-span-2">
          <h2 className="border-b border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700">
            Autores asociados
          </h2>
          {authorsQuery.isPending ? (
            <LoadingState />
          ) : authorsQuery.isError ? (
            <ErrorState
              title="No se pudieron cargar los autores"
              description={authorsQuery.error.message}
            />
          ) : (authorsQuery.data?.length ?? 0) === 0 ? (
            <EmptyState title="Sin autores asociados" />
          ) : (
            <ul className="divide-y divide-slate-100">
              {authorsQuery.data?.map((author) => (
                <li key={author.id} className="flex items-center justify-between px-4 py-3">
                  <Link
                    to={`/authors/${encodeURIComponent(author.id)}`}
                    className="text-sm font-medium text-brand-600 hover:text-brand-700"
                  >
                    {author.display_name}
                  </Link>
                  <span className="text-xs text-slate-500">{author.orcid ?? '—'}</span>
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

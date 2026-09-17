import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { institutionsApi } from '../api/endpoints'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { EmptyState, ErrorState, LoadingState } from '../components/States'

const AUTHORS_PAGE_SIZE = 15

export function InstitutionDetailPage() {
  const { institutionId = '' } = useParams()
  const [authorsPage, setAuthorsPage] = useState(1)

  const institutionQuery = useQuery({
    queryKey: ['institution', institutionId],
    queryFn: ({ signal }) => institutionsApi.get(institutionId, signal),
    enabled: Boolean(institutionId),
  })

  const authorsQuery = useQuery({
    queryKey: ['institution-authors', institutionId, authorsPage],
    queryFn: ({ signal }) =>
      institutionsApi.authors(
        institutionId,
        { page: authorsPage, page_size: AUTHORS_PAGE_SIZE },
        signal,
      ),
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

      <div className="grid items-start gap-4 lg:grid-cols-3">
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
            Investigadores asociados
          </h2>
          {authorsQuery.isPending ? (
            <LoadingState />
          ) : authorsQuery.isError ? (
            <ErrorState
              title="No se pudieron cargar los investigadores"
              description={authorsQuery.error.message}
            />
          ) : (authorsQuery.data?.total ?? 0) === 0 ? (
            <EmptyState title="Sin investigadores asociados" />
          ) : (
            <>
              <ul className="divide-y divide-slate-100">
                {authorsQuery.data?.items.map((author) => (
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
              <Pagination
                page={authorsPage}
                pageSize={AUTHORS_PAGE_SIZE}
                totalItems={authorsQuery.data?.total ?? 0}
                onPageChange={setAuthorsPage}
              />
            </>
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

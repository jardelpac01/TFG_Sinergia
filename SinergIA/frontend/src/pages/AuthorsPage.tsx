import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { authorsApi, worksApi } from '../api/endpoints'
import { PageHeader } from '../components/PageHeader'
import { Pagination } from '../components/Pagination'
import { EmptyState, ErrorState, LoadingState } from '../components/States'
import { useDebouncedValue } from '../lib/useDebouncedValue'
import { downloadBlob } from '../lib/csv'

const PAGE_SIZE = 18

export function AuthorsPage() {
  const [search, setSearch] = useState('')
  const [researchGroupId, setResearchGroupId] = useState('')
  const [fromMonth, setFromMonth] = useState('')
  const [toMonth, setToMonth] = useState('')
  const [page, setPage] = useState(1)
  const [isExporting, setIsExporting] = useState(false)
  const [exportError, setExportError] = useState<string | null>(null)
  const debouncedSearch = useDebouncedValue(search)
  const selectedResearchGroupId = researchGroupId ? Number(researchGroupId) : undefined

  const { data, isPending, isError, error } = useQuery({
    queryKey: ['authors', debouncedSearch, selectedResearchGroupId, page],
    queryFn: ({ signal }) =>
      authorsApi.list(
        {
          q: debouncedSearch,
          research_group_id: selectedResearchGroupId,
          page,
          page_size: PAGE_SIZE,
        },
        signal,
      ),
  })

  const researchGroupsQuery = useQuery({
    queryKey: ['research-groups'],
    queryFn: ({ signal }) => authorsApi.researchGroups(signal),
  })

  const authors = data?.items ?? []
  const total = data?.total ?? 0

  function handleSearchChange(value: string) {
    setSearch(value)
    setPage(1)
  }

  function handleResearchGroupChange(value: string) {
    setResearchGroupId(value)
    if (!value) {
      setFromMonth('')
      setToMonth('')
    }
    setPage(1)
    setExportError(null)
  }

  function handleExportDateChange(setter: (value: string) => void, value: string) {
    setter(value)
    setExportError(null)
  }

  async function handlePublicationsExport() {
    if (selectedResearchGroupId === undefined) return

    setIsExporting(true)
    setExportError(null)
    try {
      const blob = await worksApi.export({
        research_group_id: selectedResearchGroupId,
        author_q: debouncedSearch,
        from_month: fromMonth,
        to_month: toMonth,
      })
      const selectedGroup = researchGroupsQuery.data?.find(
        (group) => group.id === selectedResearchGroupId,
      )
      const groupLabel = selectedGroup?.code ?? selectedGroup?.name ?? 'grupo'
      const safeGroupLabel = groupLabel.replace(/[^a-zA-Z0-9_-]+/g, '-')
      downloadBlob(`publicaciones-${safeGroupLabel}.csv`, blob)
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
        title="Investigadores"
        titleClassName="text-4xl font-bold tracking-tight text-slate-900"
        actions={
          selectedResearchGroupId !== undefined ? (
            <button
              type="button"
              className="btn-primary"
              onClick={handlePublicationsExport}
              disabled={isExporting || isPending || total === 0}
            >
              {isExporting ? 'Exportando…' : 'Exportar publicaciones'}
            </button>
          ) : undefined
        }
      />

      <div className="card mb-6 grid gap-4 p-4 md:grid-cols-2">
        <div>
          <label className="label" htmlFor="author-search">
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
              id="author-search"
              className="input pl-10"
              placeholder="Ej. García, 0000-0002-…"
              value={search}
              onChange={(event) => handleSearchChange(event.target.value)}
            />
          </div>
        </div>
        <div>
          <label className="label" htmlFor="research-group">
            Grupo de investigación
          </label>
          <select
            id="research-group"
            className="input"
            value={researchGroupId}
            onChange={(event) => handleResearchGroupChange(event.target.value)}
            disabled={researchGroupsQuery.isPending || researchGroupsQuery.isError}
          >
            <option value="">Todos los grupos</option>
            {researchGroupsQuery.data?.map((group) => (
              <option key={group.id} value={group.id}>
                {group.code ? `${group.code} — ${group.name}` : group.name}
              </option>
            ))}
          </select>
        </div>
        {selectedResearchGroupId !== undefined && (
          <>
            <div>
              <label className="label" htmlFor="group-from-month">
                Publicaciones desde
              </label>
              <input
                id="group-from-month"
                type="month"
                className="input"
                value={fromMonth}
                max={toMonth || undefined}
                onChange={(event) => handleExportDateChange(setFromMonth, event.target.value)}
              />
            </div>
            <div>
              <label className="label" htmlFor="group-to-month">
                Publicaciones hasta
              </label>
              <input
                id="group-to-month"
                type="month"
                className="input"
                value={toMonth}
                min={fromMonth || undefined}
                onChange={(event) => handleExportDateChange(setToMonth, event.target.value)}
              />
            </div>
          </>
        )}
      </div>

      {researchGroupsQuery.isError && (
        <div className="mb-6">
          <ErrorState
            title="No se pudieron cargar los grupos de investigación"
            description={researchGroupsQuery.error.message}
          />
        </div>
      )}

      {exportError && (
        <div className="mb-6">
          <ErrorState title="No se pudieron exportar las publicaciones" description={exportError} />
        </div>
      )}

      {isPending ? (
        <div className="card">
          <LoadingState />
        </div>
      ) : isError ? (
        <div className="card">
          <ErrorState title="No se pudieron cargar los investigadores" description={error.message} />
        </div>
      ) : authors.length === 0 ? (
        <div className="card">
          <EmptyState
            title="Sin resultados"
            description="Prueba con otro nombre o revisa que la base de datos tenga investigadores cargados."
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
                  {author.research_group_name && (
                    <span className="badge mt-3 inline-block">
                      Grupo {author.research_group_name}
                    </span>
                  )}
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

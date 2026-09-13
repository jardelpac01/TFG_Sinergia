interface PaginationProps {
  page: number
  pageSize: number
  totalItems: number
  onPageChange: (page: number) => void
}

export function Pagination({ page, pageSize, totalItems, onPageChange }: PaginationProps) {
  const pages = Math.max(1, Math.ceil(totalItems / pageSize))
  const first = totalItems === 0 ? 0 : (page - 1) * pageSize + 1
  const last = Math.min(page * pageSize, totalItems)

  return (
    <div className="flex flex-col items-center justify-between gap-3 border-t border-slate-200 px-4 py-3 sm:flex-row">
      <p className="text-xs text-slate-500">
        Mostrando <span className="font-medium text-slate-700">{first}</span>–
        <span className="font-medium text-slate-700">{last}</span> de{' '}
        <span className="font-medium text-slate-700">{totalItems}</span>
      </p>
      <div className="flex items-center gap-2">
        <button
          type="button"
          className="btn-secondary px-3 py-1.5"
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
        >
          Anterior
        </button>
        <span className="text-xs text-slate-500">
          Página {page} de {pages}
        </span>
        <button
          type="button"
          className="btn-secondary px-3 py-1.5"
          onClick={() => onPageChange(page + 1)}
          disabled={page >= pages}
        >
          Siguiente
        </button>
      </div>
    </div>
  )
}

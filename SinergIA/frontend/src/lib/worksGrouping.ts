import type { WorkLite } from '../api/types'

export type GroupedWork<T extends WorkLite = WorkLite> = T & {
  versions: T[]
  doiList: string[]
  workIds: string[]
}

function normalizeWorkTitle(title: string): string {
  return title
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[._-]/g, ' ')
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

export function groupWorksByTitle<T extends WorkLite>(works: T[]): GroupedWork<T>[] {
  const groups = new Map<string, T[]>()

  for (const work of works) {
    const key = normalizeWorkTitle(work.title) || work.id
    groups.set(key, [...(groups.get(key) ?? []), work])
  }

  return Array.from(groups.values()).map((versions) => {
    const representative = versions.reduce((best, current) => {
      if (current.cited_by_count !== best.cited_by_count) {
        return current.cited_by_count > best.cited_by_count ? current : best
      }
      return (current.publication_year ?? 0) > (best.publication_year ?? 0) ? current : best
    }, versions[0])
    const doiList = Array.from(
      new Set(versions.map((work) => work.doi).filter((doi): doi is string => Boolean(doi)))
    )

    return {
      ...representative,
      versions,
      doiList,
      workIds: versions.map((work) => work.id),
    }
  })
}

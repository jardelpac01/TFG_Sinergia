import { apiDownload, apiGet, buildQuery } from './client'
import type {
  AuthorCollaboratorsResponse,
  AuthorLite,
  AuthorNetwork,
  Institution,
  PaginatedResponse,
  ResearchGroup,
  Topic,
  WorkDetail,
  WorkListItem,
} from './types'

export interface ListParams {
  q?: string
  limit?: number
}

export interface PaginatedListParams {
  q?: string
  research_group_id?: number
  from_month?: string
  to_month?: string
  page?: number
  page_size?: number
}

export interface WorkExportParams {
  q?: string
  author_q?: string
  author_id?: string
  research_group_id?: number
  institution_id?: string
  topic_id?: string
  from_month?: string
  to_month?: string
}

export interface WorkListParams {
  q?: string
  from_month?: string
  to_month?: string
  page?: number
  page_size?: number
}

export const authorsApi = {
  list: (params: PaginatedListParams, signal?: AbortSignal) =>
    apiGet<PaginatedResponse<AuthorLite>>(`/authors${buildQuery({ ...params })}`, signal),
  get: (id: string, signal?: AbortSignal) => apiGet<AuthorLite>(`/authors/${id}`, signal),
  works: (id: string, signal?: AbortSignal) => apiGet<WorkDetail[]>(`/authors/${id}/works`, signal),
  network: (id: string, signal?: AbortSignal) =>
    apiGet<AuthorNetwork>(`/authors/${id}/network`, signal),
  researchGroups: (signal?: AbortSignal) =>
    apiGet<ResearchGroup[]>('/authors/research-groups', signal),
  collaboratorsByName: (name: string, signal?: AbortSignal) =>
    apiGet<AuthorCollaboratorsResponse>(
      `/authors/collaborators/by-name${buildQuery({ name })}`,
      signal,
    ),
}

export const worksApi = {
  list: (params: WorkListParams, signal?: AbortSignal) =>
    apiGet<PaginatedResponse<WorkListItem>>(`/works${buildQuery({ ...params })}`, signal),
  get: (id: string, signal?: AbortSignal) => apiGet<WorkDetail>(`/works/${id}`, signal),
  export: (params: WorkExportParams, signal?: AbortSignal) =>
    apiDownload(`/works/export${buildQuery({ ...params })}`, signal),
  authors: (id: string, signal?: AbortSignal) =>
    apiGet<AuthorLite[]>(`/works/${id}/authors`, signal),
}

export const institutionsApi = {
  list: (params: PaginatedListParams, signal?: AbortSignal) =>
    apiGet<PaginatedResponse<Institution>>(`/institutions${buildQuery({ ...params })}`, signal),
  get: (id: string, signal?: AbortSignal) => apiGet<Institution>(`/institutions/${id}`, signal),
  export: (params: ListParams, signal?: AbortSignal) =>
    apiDownload(`/institutions/export${buildQuery({ ...params })}`, signal),
  authors: (id: string, params: PaginatedListParams, signal?: AbortSignal) =>
    apiGet<PaginatedResponse<AuthorLite>>(
      `/institutions/${id}/authors${buildQuery({ ...params })}`,
      signal,
    ),
}

export const topicsApi = {
  list: (params: ListParams, signal?: AbortSignal) =>
    apiGet<Topic[]>(`/topics${buildQuery({ ...params })}`, signal),
  get: (id: string, signal?: AbortSignal) => apiGet<Topic>(`/topics/${id}`, signal),
}

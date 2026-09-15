import { apiGet, buildQuery } from './client'
import type {
  AuthorCollaboratorsResponse,
  AuthorLite,
  AuthorNetwork,
  Institution,
  PaginatedResponse,
  Topic,
  WorkDetail,
  WorkLite,
} from './types'

export interface ListParams {
  q?: string
  limit?: number
}

export interface PaginatedListParams {
  q?: string
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
  collaboratorsByName: (name: string, signal?: AbortSignal) =>
    apiGet<AuthorCollaboratorsResponse>(
      `/authors/collaborators/by-name${buildQuery({ name })}`,
      signal,
    ),
}

export const worksApi = {
  list: (params: ListParams, signal?: AbortSignal) =>
    apiGet<WorkLite[]>(`/works${buildQuery({ ...params })}`, signal),
  get: (id: string, signal?: AbortSignal) => apiGet<WorkDetail>(`/works/${id}`, signal),
  authors: (id: string, signal?: AbortSignal) =>
    apiGet<AuthorLite[]>(`/works/${id}/authors`, signal),
}

export const institutionsApi = {
  list: (params: ListParams, signal?: AbortSignal) =>
    apiGet<Institution[]>(`/institutions${buildQuery({ ...params })}`, signal),
  get: (id: string, signal?: AbortSignal) => apiGet<Institution>(`/institutions/${id}`, signal),
  authors: (id: string, signal?: AbortSignal) =>
    apiGet<AuthorLite[]>(`/institutions/${id}/authors`, signal),
}

export const topicsApi = {
  list: (params: ListParams, signal?: AbortSignal) =>
    apiGet<Topic[]>(`/topics${buildQuery({ ...params })}`, signal),
  get: (id: string, signal?: AbortSignal) => apiGet<Topic>(`/topics/${id}`, signal),
}

export interface AuthorLite {
  id: string
  display_name: string
  orcid: string | null
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface Institution {
  id: string
  name: string
  country_code: string | null
  ror: string | null
  type: string | null
  geo_lat: number | null
  geo_lon: number | null
  city: string | null
  updated_at: string
}

export interface Topic {
  id: string
  display_name: string
  subfield: string | null
  field: string | null
  domain: string | null
}

export interface Source {
  id: string
  display_name?: string | null
  [key: string]: unknown
}

export interface WorkLite {
  id: string
  title: string
  publication_year: number | null
  publication_date: string | null
  language: string | null
  doi: string | null
  cited_by_count: number
  is_oa: boolean
  oa_status: string | null
  is_retracted: boolean
  type: string | null
  source_id: string | null
}

export interface WorkDetail extends WorkLite {
  updated_at: string
  source: Source | null
  topics: Topic[]
  authors: AuthorLite[]
}

export interface CoAuthorConnection {
  id: string
  display_name: string
  shared_works_count: number
}

export interface CountryConnection {
  country_code: string | null
  works_count: number
}

export interface AuthorNetwork {
  author: AuthorLite
  coauthors: CoAuthorConnection[]
  country_collaborations: CountryConnection[]
}

export interface CoAuthorLocation {
  id: string
  display_name: string
  orcid: string | null
  shared_works_count: number
  institution_name: string | null
  country_code: string | null
  city: string | null
}

export interface AuthorCollaboratorsResponse {
  author: AuthorLite
  collaborators: CoAuthorLocation[]
}

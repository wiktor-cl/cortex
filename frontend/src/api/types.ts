export type Role = 'USER' | 'ADMIN'

export type DocumentStatus = 'QUEUED' | 'PROCESSING' | 'DONE' | 'FAILED'

export interface AuthResponse {
  token: string
  userId: string
  email: string
  role: Role
}

export interface Collection {
  id: string
  name: string
  description: string | null
  ownerId: string
  createdAt: string
}

export interface Document {
  id: string
  collectionId: string
  filename: string
  uploadedBy: string
  status: DocumentStatus
  chunkCount: number
  errorMessage: string | null
  uploadedAt: string
}

export interface Citation {
  documentId: string
  filename: string
  pageNumber: number | null
  chunkIndex: number
  snippet: string
  score: number
}

export interface SubAnswer {
  subQuestion: string
  toolUsed: string | null
  answer: string
  citations: Citation[]
}

export interface QueryResponse {
  queryId: string
  answer: string
  mode: string
  citations: Citation[]
  subAnswers: SubAnswer[]
}

export interface QueryHistoryEntry {
  id: string
  collectionId: string | null
  question: string
  answer: string
  mode: string
  citations: Citation[]
  createdAt: string
}

export interface AdminStats {
  userCount: number
  collectionCount: number
  documentCount: number
  queryCount: number
  documentsByStatus: Record<string, number>
}

export interface AdminUser {
  id: string
  email: string
  role: Role
  createdAt: string
}

export interface ProblemDetail {
  type?: string
  title?: string
  status?: number
  detail?: string
  instance?: string
}

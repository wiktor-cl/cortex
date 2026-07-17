import { useEffect, useRef, useState, type FormEvent } from 'react'
import { api, ApiError } from '../api/client'
import { StatusBadge } from '../components/StatusBadge'
import type { Collection, Document } from '../api/types'

const ACTIVE_STATUSES = new Set(['QUEUED', 'PROCESSING'])

export function CollectionsPage() {
  const [collections, setCollections] = useState<Collection[]>([])
  const [selected, setSelected] = useState<Collection | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [newName, setNewName] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const loadCollections = async () => {
    const result = await api.get<Collection[]>('/collections')
    setCollections(result)
    return result
  }

  const loadDocuments = async (collectionId: string) => {
    const result = await api.get<Document[]>(`/collections/${collectionId}/documents`)
    setDocuments(result)
    return result
  }

  useEffect(() => {
    loadCollections().catch(() => undefined)
  }, [])

  useEffect(() => {
    if (!selected) return
    loadDocuments(selected.id).catch(() => undefined)
  }, [selected])

  useEffect(() => {
    if (!selected || !documents.some((doc) => ACTIVE_STATUSES.has(doc.status))) return
    const interval = window.setInterval(() => {
      loadDocuments(selected.id).catch(() => undefined)
    }, 3000)
    return () => window.clearInterval(interval)
  }, [selected, documents])

  const onCreateCollection = async (event: FormEvent) => {
    event.preventDefault()
    setError(null)
    try {
      const created = await api.post<Collection>('/collections', {
        name: newName,
        description: newDescription || null,
      })
      setNewName('')
      setNewDescription('')
      await loadCollections()
      setSelected(created)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to create collection')
    }
  }

  const onDeleteCollection = async (collection: Collection) => {
    await api.delete(`/collections/${collection.id}`)
    if (selected?.id === collection.id) setSelected(null)
    await loadCollections()
  }

  const onUpload = async (event: FormEvent) => {
    event.preventDefault()
    if (!selected) return
    const file = fileInputRef.current?.files?.[0]
    if (!file) return
    setError(null)
    try {
      await api.upload<Document>(`/collections/${selected.id}/documents`, file)
      if (fileInputRef.current) fileInputRef.current.value = ''
      await loadDocuments(selected.id)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Upload failed')
    }
  }

  const onDeleteDocument = async (document: Document) => {
    if (!selected) return
    await api.delete(`/documents/${document.id}`)
    await loadDocuments(selected.id)
  }

  return (
    <div className="mx-auto grid h-full max-w-5xl grid-cols-[220px_1fr] gap-6 px-4 py-6">
      <div>
        <h1 className="mb-4 text-xl font-semibold">Collections</h1>

        <form onSubmit={onCreateCollection} className="mb-4 flex flex-col gap-2">
          <input
            value={newName}
            onChange={(event) => setNewName(event.target.value)}
            placeholder="Name"
            required
            className="rounded-lg border border-slate-300 bg-transparent px-2 py-1.5 text-sm dark:border-slate-700"
          />
          <input
            value={newDescription}
            onChange={(event) => setNewDescription(event.target.value)}
            placeholder="Description (optional)"
            className="rounded-lg border border-slate-300 bg-transparent px-2 py-1.5 text-sm dark:border-slate-700"
          />
          <button
            type="submit"
            className="rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-500"
          >
            New collection
          </button>
        </form>

        <ul className="space-y-1">
          {collections.map((collection) => (
            <li key={collection.id}>
              <button
                onClick={() => setSelected(collection)}
                className={`w-full truncate rounded-lg px-2 py-1.5 text-left text-sm ${
                  selected?.id === collection.id
                    ? 'bg-indigo-600 text-white'
                    : 'text-slate-600 hover:bg-slate-200/60 dark:text-slate-300 dark:hover:bg-slate-800'
                }`}
              >
                {collection.name}
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div>
        {error && <p className="mb-3 text-sm text-rose-600 dark:text-rose-400">{error}</p>}

        {!selected ? (
          <p className="text-sm text-slate-400">Select or create a collection to manage its documents.</p>
        ) : (
          <>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold">{selected.name}</h2>
                {selected.description && (
                  <p className="text-sm text-slate-500 dark:text-slate-400">{selected.description}</p>
                )}
              </div>
              <button
                onClick={() => onDeleteCollection(selected)}
                className="rounded-lg px-3 py-1.5 text-sm text-rose-600 hover:bg-rose-50 dark:text-rose-400 dark:hover:bg-rose-950/40"
              >
                Delete collection
              </button>
            </div>

            <form onSubmit={onUpload} className="mb-4 flex items-center gap-2">
              <input
                ref={fileInputRef}
                type="file"
                required
                className="flex-1 text-sm file:mr-3 file:rounded-lg file:border-0 file:bg-slate-200 file:px-3 file:py-1.5 file:text-sm dark:file:bg-slate-800"
              />
              <button
                type="submit"
                className="rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-500"
              >
                Upload
              </button>
            </form>

            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 dark:border-slate-800 dark:text-slate-400">
                  <th className="py-2 font-medium">File</th>
                  <th className="py-2 font-medium">Status</th>
                  <th className="py-2 font-medium">Chunks</th>
                  <th className="py-2 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {documents.map((document) => (
                  <tr key={document.id} className="border-b border-slate-100 dark:border-slate-900">
                    <td className="py-2">
                      {document.filename}
                      {document.status === 'FAILED' && document.errorMessage && (
                        <p className="text-xs text-rose-500">{document.errorMessage}</p>
                      )}
                    </td>
                    <td className="py-2">
                      <StatusBadge status={document.status} />
                    </td>
                    <td className="py-2">{document.chunkCount}</td>
                    <td className="py-2 text-right">
                      <button
                        onClick={() => onDeleteDocument(document)}
                        className="text-slate-400 hover:text-rose-600 dark:hover:text-rose-400"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
                {documents.length === 0 && (
                  <tr>
                    <td colSpan={4} className="py-4 text-center text-slate-400">
                      No documents yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </>
        )}
      </div>
    </div>
  )
}

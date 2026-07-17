import { useEffect, useRef, useState, type FormEvent } from 'react'
import { api, ApiError } from '../api/client'
import { CitationList } from '../components/CitationList'
import type { Citation, Collection, QueryHistoryEntry, QueryResponse, SubAnswer } from '../api/types'

interface Exchange {
  id: string
  question: string
  answer: string
  mode: string
  citations: Citation[]
  subAnswers: SubAnswer[]
}

function fromHistory(entry: QueryHistoryEntry): Exchange {
  return {
    id: entry.id,
    question: entry.question,
    answer: entry.answer,
    mode: entry.mode,
    citations: entry.citations,
    subAnswers: [],
  }
}

function fromResponse(question: string, response: QueryResponse): Exchange {
  return {
    id: response.queryId,
    question,
    answer: response.answer,
    mode: response.mode,
    citations: response.citations,
    subAnswers: response.subAnswers,
  }
}

export function ChatPage() {
  const [collections, setCollections] = useState<Collection[]>([])
  const [collectionId, setCollectionId] = useState<string>('')
  const [question, setQuestion] = useState('')
  const [exchanges, setExchanges] = useState<Exchange[]>([])
  const [asking, setAsking] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    api.get<Collection[]>('/collections').then(setCollections).catch(() => undefined)
    api
      .get<QueryHistoryEntry[]>('/query/history')
      .then((history) => setExchanges(history.map(fromHistory).reverse()))
      .catch(() => undefined)
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [exchanges, asking])

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const trimmed = question.trim()
    if (!trimmed || asking) return

    setError(null)
    setAsking(true)
    setQuestion('')
    try {
      const response = await api.post<QueryResponse>('/query', {
        question: trimmed,
        collectionId: collectionId || null,
        topK: 5,
      })
      setExchanges((current) => [...current, fromResponse(trimmed, response)])
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to get an answer')
      setQuestion(trimmed)
    } finally {
      setAsking(false)
    }
  }

  return (
    <div className="mx-auto flex h-full max-w-3xl flex-col px-4 py-6">
      <div className="mb-4 flex items-center justify-between gap-4">
        <h1 className="text-xl font-semibold">Chat</h1>
        <select
          value={collectionId}
          onChange={(event) => setCollectionId(event.target.value)}
          className="rounded-lg border border-slate-300 bg-transparent px-3 py-1.5 text-sm dark:border-slate-700"
        >
          <option value="">All collections</option>
          {collections.map((collection) => (
            <option key={collection.id} value={collection.id}>
              {collection.name}
            </option>
          ))}
        </select>
      </div>

      <div className="flex-1 space-y-6 overflow-y-auto pr-1">
        {exchanges.length === 0 && !asking && (
          <p className="mt-12 text-center text-sm text-slate-400">
            Ask a question about your documentation to get started.
          </p>
        )}

        {exchanges.map((exchange) => (
          <div key={exchange.id} className="space-y-3">
            <div className="ml-auto max-w-[80%] rounded-2xl rounded-tr-sm bg-indigo-600 px-4 py-2 text-sm text-white">
              {exchange.question}
            </div>

            <div className="max-w-[85%] rounded-2xl rounded-tl-sm border border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-900">
              <div className="mb-2 flex items-center gap-2">
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                  {exchange.mode}
                </span>
              </div>
              <p className="whitespace-pre-wrap text-sm text-slate-800 dark:text-slate-100">{exchange.answer}</p>
              <CitationList citations={exchange.citations} />

              {exchange.subAnswers.length > 0 && (
                <div className="mt-3 space-y-2 border-t border-slate-200 pt-3 dark:border-slate-800">
                  <span className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                    Agent steps
                  </span>
                  {exchange.subAnswers.map((sub, index) => (
                    <div key={index} className="rounded-lg bg-slate-50 p-2 text-xs dark:bg-slate-800/60">
                      <p className="font-medium text-slate-600 dark:text-slate-300">
                        {sub.toolUsed ? `[${sub.toolUsed}] ` : ''}
                        {sub.subQuestion}
                      </p>
                      <p className="mt-1 text-slate-500 dark:text-slate-400">{sub.answer}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {asking && (
          <div className="max-w-[85%] rounded-2xl rounded-tl-sm border border-slate-200 bg-white px-4 py-3 text-sm text-slate-400 dark:border-slate-800 dark:bg-slate-900">
            Thinking…
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && <p className="mt-3 text-sm text-rose-600 dark:text-rose-400">{error}</p>}

      <form onSubmit={onSubmit} className="mt-4 flex gap-2">
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask about your documentation…"
          className="flex-1 rounded-lg border border-slate-300 bg-transparent px-3 py-2 text-sm outline-none focus:border-indigo-500 dark:border-slate-700"
        />
        <button
          type="submit"
          disabled={asking || !question.trim()}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-500 disabled:opacity-60"
        >
          Send
        </button>
      </form>
    </div>
  )
}

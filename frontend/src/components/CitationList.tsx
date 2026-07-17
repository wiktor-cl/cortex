import type { Citation } from '../api/types'

export function CitationList({ citations }: { citations: Citation[] }) {
  if (citations.length === 0) return null

  return (
    <div className="mt-3 flex flex-col gap-2">
      <span className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
        Sources
      </span>
      <ol className="flex flex-col gap-2">
        {citations.map((citation, index) => (
          <li
            key={`${citation.documentId}-${citation.chunkIndex}`}
            className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm dark:border-slate-800 dark:bg-slate-900"
          >
            <div className="mb-1 flex items-center justify-between gap-2">
              <span className="font-medium text-slate-700 dark:text-slate-200">
                [{index + 1}] {citation.filename}
                {citation.pageNumber !== null ? ` — p.${citation.pageNumber}` : ''}
              </span>
              <span className="shrink-0 text-xs text-slate-400">
                score {citation.score.toFixed(2)}
              </span>
            </div>
            <p className="text-slate-600 dark:text-slate-400">{citation.snippet}</p>
          </li>
        ))}
      </ol>
    </div>
  )
}

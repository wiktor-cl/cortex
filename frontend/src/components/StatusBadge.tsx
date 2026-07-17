import type { DocumentStatus } from '../api/types'

const STYLES: Record<DocumentStatus, string> = {
  QUEUED: 'bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
  PROCESSING: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300',
  DONE: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300',
  FAILED: 'bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300',
}

export function StatusBadge({ status }: { status: DocumentStatus }) {
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STYLES[status]}`}>
      {status.toLowerCase()}
    </span>
  )
}

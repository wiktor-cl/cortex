import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { AdminStats, AdminUser, Role } from '../api/types'

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
    </div>
  )
}

export function AdminPage() {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [users, setUsers] = useState<AdminUser[]>([])

  const reload = () => {
    api.get<AdminStats>('/admin/stats').then(setStats).catch(() => undefined)
    api.get<AdminUser[]>('/admin/users').then(setUsers).catch(() => undefined)
  }

  useEffect(reload, [])

  const changeRole = async (user: AdminUser, role: Role) => {
    await api.patch(`/admin/users/${user.id}/role`, { role })
    reload()
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-6">
      <h1 className="mb-4 text-xl font-semibold">Admin</h1>

      {stats && (
        <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard label="Users" value={stats.userCount} />
          <StatCard label="Collections" value={stats.collectionCount} />
          <StatCard label="Documents" value={stats.documentCount} />
          <StatCard label="Queries" value={stats.queryCount} />
        </div>
      )}

      {stats && (
        <div className="mb-8 flex flex-wrap gap-2">
          {Object.entries(stats.documentsByStatus).map(([status, count]) => (
            <span
              key={status}
              className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300"
            >
              {status.toLowerCase()}: {count}
            </span>
          ))}
        </div>
      )}

      <h2 className="mb-3 text-lg font-semibold">Users</h2>
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-slate-500 dark:border-slate-800 dark:text-slate-400">
            <th className="py-2 font-medium">Email</th>
            <th className="py-2 font-medium">Role</th>
            <th className="py-2 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id} className="border-b border-slate-100 dark:border-slate-900">
              <td className="py-2">{user.email}</td>
              <td className="py-2">
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium dark:bg-slate-800">
                  {user.role}
                </span>
              </td>
              <td className="py-2 text-right">
                <button
                  onClick={() => changeRole(user, user.role === 'ADMIN' ? 'USER' : 'ADMIN')}
                  className="text-xs font-medium text-indigo-600 hover:underline dark:text-indigo-400"
                >
                  Make {user.role === 'ADMIN' ? 'USER' : 'ADMIN'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

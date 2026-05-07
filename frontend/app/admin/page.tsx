import { revalidatePath } from "next/cache"
import { redirect } from "next/navigation"
import { auth } from "@/auth"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
const ADMIN_EMAIL = process.env.ADMIN_EMAIL ?? "lbarretti@gmail.com"

interface UserRow {
  id: number
  email: string
  name: string | null
  picture: string | null
  status: "pending" | "approved" | "rejected"
  created_at: string
}

async function fetchUsers(adminEmail: string, filterStatus?: string): Promise<UserRow[]> {
  const url = filterStatus
    ? `${API_URL}/admin/users?filter_status=${filterStatus}`
    : `${API_URL}/admin/users`

  const res = await fetch(url, {
    headers: { "X-Admin-Email": adminEmail },
    cache: "no-store",
  })

  if (!res.ok) return []
  return res.json()
}

const STATUS_LABEL: Record<string, string> = {
  pending: "Pending",
  approved: "Approved",
  rejected: "Rejected",
}

const STATUS_COLOR: Record<string, string> = {
  pending: "text-yellow-400 bg-yellow-400/10",
  approved: "text-green-400 bg-green-400/10",
  rejected: "text-red-400 bg-red-400/10",
}

export default async function AdminPage({
  searchParams,
}: {
  searchParams: Promise<{ status?: string }>
}) {
  const session = await auth()

  if (!session?.user?.email || session.user.email !== ADMIN_EMAIL) {
    redirect("/")
  }

  const params = await searchParams
  const activeStatus = params.status ?? "pending"
  const users = await fetchUsers(session.user.email, activeStatus)

  async function approve(formData: FormData) {
    "use server"
    const session = await auth()
    if (!session?.user?.email) return
    const id = formData.get("id") as string
    await fetch(`${API_URL}/admin/users/${id}/approve`, {
      method: "POST",
      headers: { "X-Admin-Email": session.user.email },
    })
    revalidatePath("/admin")
  }

  async function reject(formData: FormData) {
    "use server"
    const session = await auth()
    if (!session?.user?.email) return
    const id = formData.get("id") as string
    await fetch(`${API_URL}/admin/users/${id}/reject`, {
      method: "POST",
      headers: { "X-Admin-Email": session.user.email },
    })
    revalidatePath("/admin")
  }

  return (
    <div className="min-h-screen bg-neutral-950 px-6 py-10">
      <div className="mx-auto max-w-3xl">
        <div className="mb-8">
          <h1 className="text-xl font-semibold text-neutral-100">User Management</h1>
          <p className="mt-1 text-sm text-neutral-500">
            Review and approve access requests
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6 flex gap-2">
          {(["pending", "approved", "rejected"] as const).map((s) => (
            <a
              key={s}
              href={`/admin?status=${s}`}
              className={`rounded-lg px-4 py-2 text-sm transition ${
                activeStatus === s
                  ? "bg-neutral-800 text-neutral-100"
                  : "text-neutral-500 hover:text-neutral-300"
              }`}
            >
              {STATUS_LABEL[s]}
            </a>
          ))}
        </div>

        {/* User list */}
        {users.length === 0 ? (
          <p className="text-sm text-neutral-600">No {activeStatus} users.</p>
        ) : (
          <ul className="space-y-3">
            {users.map((user) => (
              <li
                key={user.id}
                className="flex items-center justify-between rounded-xl border border-neutral-800 bg-neutral-900 px-5 py-4"
              >
                <div className="flex items-center gap-3">
                  {user.picture ? (
                    <img
                      src={user.picture}
                      alt={user.name ?? user.email}
                      className="h-9 w-9 rounded-full"
                    />
                  ) : (
                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-neutral-700 text-xs text-neutral-400">
                      {(user.name ?? user.email)[0].toUpperCase()}
                    </div>
                  )}
                  <div>
                    <p className="text-sm font-medium text-neutral-200">
                      {user.name ?? "—"}
                    </p>
                    <p className="text-xs text-neutral-500">{user.email}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span
                    className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COLOR[user.status]}`}
                  >
                    {STATUS_LABEL[user.status]}
                  </span>

                  {user.status === "pending" && (
                    <div className="flex gap-2">
                      <form action={approve}>
                        <input type="hidden" name="id" value={user.id} />
                        <button
                          type="submit"
                          className="rounded-lg bg-green-500/10 px-3 py-1.5 text-xs font-medium text-green-400 transition hover:bg-green-500/20"
                        >
                          Approve
                        </button>
                      </form>
                      <form action={reject}>
                        <input type="hidden" name="id" value={user.id} />
                        <button
                          type="submit"
                          className="rounded-lg bg-red-500/10 px-3 py-1.5 text-xs font-medium text-red-400 transition hover:bg-red-500/20"
                        >
                          Reject
                        </button>
                      </form>
                    </div>
                  )}

                  {user.status === "approved" && (
                    <form action={reject}>
                      <input type="hidden" name="id" value={user.id} />
                      <button
                        type="submit"
                        className="rounded-lg bg-red-500/10 px-3 py-1.5 text-xs font-medium text-red-400 transition hover:bg-red-500/20"
                      >
                        Revoke
                      </button>
                    </form>
                  )}

                  {user.status === "rejected" && (
                    <form action={approve}>
                      <input type="hidden" name="id" value={user.id} />
                      <button
                        type="submit"
                        className="rounded-lg bg-green-500/10 px-3 py-1.5 text-xs font-medium text-green-400 transition hover:bg-green-500/20"
                      >
                        Approve
                      </button>
                    </form>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

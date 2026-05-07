import { auth, signOut } from "@/auth"

const ADMIN_EMAIL = process.env.ADMIN_EMAIL ?? "lbarretti@gmail.com"

export async function Header() {
  const session = await auth()
  const isAdmin = session?.user?.email === ADMIN_EMAIL

  return (
    <header className="border-b border-neutral-800 bg-neutral-950 px-6 py-4">
      <div className="mx-auto flex max-w-4xl items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-neutral-100">Ask the Classics</h1>
          <p className="text-xs text-neutral-500">The Wealth of Nations — Adam Smith (1776)</p>
        </div>

        <div className="flex items-center gap-4">
          <a
            href="https://github.com/leopbar/rag-portfolio"
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-neutral-500 transition hover:text-neutral-300"
          >
            GitHub →
          </a>

          {isAdmin && (
            <a
              href="/admin"
              className="text-xs text-neutral-500 transition hover:text-neutral-300"
            >
              Admin →
            </a>
          )}

          {session?.user && (
            <div className="flex items-center gap-3">
              {session.user.image && (
                <img
                  src={session.user.image}
                  alt={session.user.name ?? "User"}
                  className="h-7 w-7 rounded-full"
                />
              )}
              <span className="text-xs text-neutral-400">{session.user.name}</span>
              <form
                action={async () => {
                  "use server"
                  await signOut({ redirectTo: "/login" })
                }}
              >
                <button
                  type="submit"
                  className="text-xs text-neutral-500 transition hover:text-red-400"
                >
                  Sign out
                </button>
              </form>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

import { signIn } from "@/auth"

export default function PendingPage() {
  return (
    <div className="flex h-screen flex-col items-center justify-center bg-neutral-950">
      <div className="w-full max-w-sm rounded-2xl border border-neutral-800 bg-neutral-900 p-8 text-center">
        <div className="mb-4 flex justify-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-yellow-500/10">
            <svg
              className="h-6 w-6 text-yellow-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
        </div>

        <h1 className="text-xl font-semibold text-neutral-100">Access Pending</h1>
        <p className="mt-2 text-sm text-neutral-500">
          Ask the Classics — The Wealth of Nations
        </p>

        <p className="mt-6 text-sm text-neutral-400">
          Your access request has been submitted. The administrator will review
          it shortly.
        </p>

        <p className="mt-2 text-xs text-neutral-600">
          Once approved, sign in again to start chatting.
        </p>

        <form
          className="mt-8"
          action={async () => {
            "use server"
            await signIn("google", { redirectTo: "/" })
          }}
        >
          <button
            type="submit"
            className="w-full rounded-xl border border-neutral-700 px-4 py-2.5 text-sm text-neutral-400 transition hover:border-neutral-500 hover:text-neutral-200"
          >
            Try signing in again
          </button>
        </form>
      </div>
    </div>
  )
}

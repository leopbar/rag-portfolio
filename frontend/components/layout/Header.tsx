export function Header() {
  return (
    <header className="border-b border-neutral-800 bg-neutral-950 px-6 py-4">
      <div className="mx-auto flex max-w-4xl items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-neutral-100">Ask the Classics</h1>
          <p className="text-xs text-neutral-500">The Wealth of Nations — Adam Smith (1776)</p>
        </div>
        <a
          href="https://github.com/leopbar/rag-portfolio"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-neutral-500 transition hover:text-neutral-300"
        >
          GitHub →
        </a>
      </div>
    </header>
  )
}

"use client"

import { useState } from "react"
import type { SourceInfo } from "@/lib/api-client"

interface SourceCardProps {
  source: SourceInfo
  index: number
}

export function SourceCard({ source, index }: SourceCardProps) {
  const [expanded, setExpanded] = useState(false)

  const label = source.section
    ? `${source.book}, ${source.chapter} — ${source.section}`
    : `${source.book}, ${source.chapter}`

  return (
    <button
      onClick={() => setExpanded((prev) => !prev)}
      className="w-full text-left rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm transition hover:border-neutral-500"
    >
      <div className="flex items-center justify-between gap-2">
        <span className="font-medium text-neutral-200">
          [{index}] {label}
        </span>
        <span className="shrink-0 text-xs text-neutral-500">
          score {source.score.toFixed(3)} {expanded ? "▲" : "▼"}
        </span>
      </div>
    </button>
  )
}

"use client"

import { useRef, useEffect, useState } from "react"
import { useChat } from "@/hooks/useChat"
import { MessageBubble } from "./MessageBubble"
import { SourceCard } from "./SourceCard"

export function ChatWindow() {
  const { messages, sources, isLoading, sendMessage } = useChat()
  const [input, setInput] = useState("")
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const question = input.trim()
    if (!question || isLoading) return
    setInput("")
    await sendMessage(question)
  }

  return (
    <div className="flex h-full flex-col gap-4">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto rounded-xl border border-neutral-700 bg-neutral-900 p-4">
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center text-center text-neutral-500">
            <div>
              <p className="text-lg font-medium text-neutral-300">Ask the Classics</p>
              <p className="mt-1 text-sm">
                Ask anything about Adam Smith&apos;s The Wealth of Nations
              </p>
              <p className="mt-4 text-xs text-neutral-600">
                Try: &quot;What does Smith say about the division of labour?&quot;
              </p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {messages.map((msg, i) => (
              <MessageBubble key={i} message={msg} />
            ))}
            {isLoading && messages[messages.length - 1]?.role === "assistant" &&
              messages[messages.length - 1]?.content === "" && (
                <div className="flex justify-start">
                  <div className="rounded-2xl bg-neutral-800 px-4 py-3 text-sm text-neutral-400">
                    Searching sources…
                  </div>
                </div>
              )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Sources */}
      {sources.length > 0 && (
        <div className="flex flex-col gap-2">
          <p className="text-xs font-medium uppercase tracking-wider text-neutral-500">
            Sources cited
          </p>
          <div className="flex flex-col gap-1">
            {sources.map((source, i) => (
              <SourceCard key={source.id} source={source} index={i + 1} />
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about The Wealth of Nations…"
          disabled={isLoading}
          className="flex-1 rounded-xl border border-neutral-700 bg-neutral-800 px-4 py-3 text-sm text-neutral-100 placeholder-neutral-500 outline-none focus:border-blue-500 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-blue-500 disabled:opacity-40"
        >
          Send
        </button>
      </form>
    </div>
  )
}

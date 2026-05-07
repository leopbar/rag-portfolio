"use client"

import { useState, useCallback } from "react"
import { API_URL, type Message, type SourceInfo } from "@/lib/api-client"

interface UseChatReturn {
  messages: Message[]
  sources: SourceInfo[]
  isLoading: boolean
  sendMessage: (question: string) => Promise<void>
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([])
  const [sources, setSources] = useState<SourceInfo[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = useCallback(async (question: string) => {
    setIsLoading(true)
    setSources([])

    const userMessage: Message = { role: "user", content: question }
    setMessages((prev) => [...prev, userMessage])

    const assistantMessage: Message = { role: "assistant", content: "" }
    setMessages((prev) => [...prev, assistantMessage])

    try {
      const response = await fetch(`${API_URL}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          history: messages,
        }),
      })

      if (!response.body) throw new Error("No response body")

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value)
        const lines = text.split("\n").filter((l) => l.startsWith("data: "))

        for (const line of lines) {
          const data = line.slice(6) // remove "data: "

          if (data === "[DONE]") break

          if (data.startsWith("[SOURCES]")) {
            const json = data.slice(10) // remove "[SOURCES] "
            setSources(JSON.parse(json))
            continue
          }

          setMessages((prev) => {
            const updated = [...prev]
            const last = updated[updated.length - 1]
            updated[updated.length - 1] = {
              ...last,
              content: last.content + data,
            }
            return updated
          })
        }
      }
    } finally {
      setIsLoading(false)
    }
  }, [messages])

  return { messages, sources, isLoading, sendMessage }
}

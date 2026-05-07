export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export interface SourceInfo {
  id: number
  book: string
  chapter: string
  section: string | null
  score: number
}

export interface Message {
  role: "user" | "assistant"
  content: string
}

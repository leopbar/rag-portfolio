import { ChatWindow } from "@/components/chat/ChatWindow"
import { Header } from "@/components/layout/Header"

export default function Home() {
  return (
    <div className="flex h-screen flex-col bg-neutral-950 text-neutral-100">
      <Header />
      <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col overflow-hidden p-4">
        <ChatWindow />
      </main>
    </div>
  )
}

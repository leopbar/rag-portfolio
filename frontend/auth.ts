import NextAuth from "next-auth"
import Google from "next-auth/providers/google"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  pages: {
    signIn: "/login",
  },
  callbacks: {
    async signIn({ user }) {
      try {
        const res = await fetch(`${API_URL}/users/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: user.email,
            name: user.name,
            picture: user.image,
          }),
        })

        if (!res.ok) return "/login?error=ServerError"

        const data: { status: string; is_admin: boolean } = await res.json()

        if (data.status === "approved") return true
        if (data.status === "pending") return "/pending"
        return "/login?error=AccessDenied"
      } catch {
        return "/login?error=ServerError"
      }
    },

    async session({ session, token }) {
      if (token.sub) session.user.id = token.sub
      return session
    },
  },
})

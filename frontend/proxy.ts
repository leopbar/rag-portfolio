import { auth } from "@/auth"
import { NextResponse } from "next/server"

const ADMIN_EMAIL = process.env.ADMIN_EMAIL ?? "lbarretti@gmail.com"

export default auth((req) => {
  const { pathname } = req.nextUrl
  const isLoggedIn = !!req.auth
  const userEmail = req.auth?.user?.email ?? ""

  // Páginas públicas (sem sessão necessária)
  const isPublicPage =
    pathname === "/login" ||
    pathname === "/pending" ||
    pathname.startsWith("/api/auth")

  if (!isLoggedIn && !isPublicPage) {
    return NextResponse.redirect(new URL("/login", req.nextUrl.origin))
  }

  // Usuário logado tentando acessar login → home
  if (isLoggedIn && pathname === "/login") {
    return NextResponse.redirect(new URL("/", req.nextUrl.origin))
  }

  // Rota /admin: só admin passa
  if (pathname.startsWith("/admin")) {
    if (!isLoggedIn || userEmail !== ADMIN_EMAIL) {
      return NextResponse.redirect(new URL("/", req.nextUrl.origin))
    }
  }
})

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
}

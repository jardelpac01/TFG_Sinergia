import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'

export function Layout() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50">
      <aside
        className={`relative flex flex-col border-r border-slate-200 bg-white transition-all duration-300 ease-in-out ${
          collapsed ? 'w-20' : 'w-64'
        }`}
      >
        <button
          type="button"
          onClick={() => setCollapsed(!collapsed)}
          title={collapsed ? 'Expandir menú' : 'Colapsar menú'}
          className="absolute -right-3.5 top-1/2 z-20 flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-500 shadow-sm transition-all hover:bg-slate-50 hover:text-slate-900 hover:shadow"
        >
          <svg
            className={`h-4 w-4 transition-transform duration-300 ${
              collapsed ? 'rotate-180' : ''
            }`}
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <div className={`flex h-24 items-center justify-center ${collapsed ? 'px-2' : 'px-4'}`}>
          <NavLink
            to="/"
            className={`flex items-center overflow-hidden ${
              collapsed ? 'w-full justify-center' : 'w-full justify-center gap-3'
            }`}
          >
            <img
              src="/logo.jpg"
              alt="Logo SinergIA"
              className="h-16 w-16 shrink-0 rounded-xl object-contain"
            />
            {!collapsed && (
              <span className="whitespace-nowrap font-display text-2xl font-light text-slate-900">
                SinergIA
              </span>
            )}
          </NavLink>
        </div>

        <nav className="flex-1 space-y-2 px-3 py-4">
          <NavLink
            to="/authors"
            title="Autores"
            className={({ isActive }) =>
              `group flex items-center gap-3.5 rounded-xl px-3.5 py-3 text-sm font-medium transition-all ${
                collapsed ? 'justify-center' : ''
              } ${
                isActive
                  ? 'bg-brand-50 text-brand-700 font-semibold shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`
            }
          >
            <svg
              className="h-6 w-6 shrink-0"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            {!collapsed && <span className="whitespace-nowrap">Autores</span>}
          </NavLink>

          <NavLink
            to="/works"
            title="Publicaciones"
            className={({ isActive }) =>
              `group flex items-center gap-3.5 rounded-xl px-3.5 py-3 text-sm font-medium transition-all ${
                collapsed ? 'justify-center' : ''
              } ${
                isActive
                  ? 'bg-brand-50 text-brand-700 font-semibold shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`
            }
          >
            <svg
              className="h-6 w-6 shrink-0"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              />
            </svg>
            {!collapsed && <span className="whitespace-nowrap">Publicaciones</span>}
          </NavLink>
        </nav>
      </aside>

      <div className="flex flex-1 flex-col overflow-y-auto">
        <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
          <Outlet />
        </main>
        <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-400">
          SinergIA © 2026
        </footer>
      </div>
    </div>
  )
}

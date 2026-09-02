import { Construction } from 'lucide-react'

export function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-slate-300 py-24 text-center">
      <span className="flex h-12 w-12 items-center justify-center rounded-full bg-sapphire-50">
        <Construction className="h-6 w-6 text-sapphire-600" aria-hidden />
      </span>
      <h2 className="text-base font-semibold text-slate-900">{title}</h2>
      <p className="max-w-sm text-sm text-slate-500">
        Este módulo será implementado em uma próxima etapa do frontend.
      </p>
    </div>
  )
}

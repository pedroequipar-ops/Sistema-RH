import type { HTMLAttributes } from 'react'

import { cn } from '@/lib/cn'

type Tone = 'sapphire' | 'slate' | 'green' | 'red' | 'amber'

const toneClasses: Record<Tone, string> = {
  sapphire: 'bg-sapphire-50 text-sapphire-700 border-sapphire-200',
  slate: 'bg-slate-100 text-slate-600 border-slate-200',
  green: 'bg-green-50 text-green-700 border-green-200',
  red: 'bg-red-50 text-red-700 border-red-200',
  amber: 'bg-amber-50 text-amber-700 border-amber-200',
}

export function Badge({
  tone = 'slate',
  className,
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: Tone }) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium',
        toneClasses[tone],
        className,
      )}
      {...props}
    />
  )
}

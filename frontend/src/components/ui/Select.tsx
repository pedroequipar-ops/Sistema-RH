import { ChevronDown } from 'lucide-react'
import { type SelectHTMLAttributes, forwardRef } from 'react'

import { cn } from '@/lib/cn'

type SelectProps = SelectHTMLAttributes<HTMLSelectElement>

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div className="relative">
        <select
          ref={ref}
          className={cn(
            'w-full appearance-none rounded-lg border border-slate-300 bg-white px-3 py-2 pr-9 text-sm text-slate-800',
            'focus:outline-none focus:ring-2 focus:ring-sapphire-400 focus:border-sapphire-400',
            className,
          )}
          {...props}
        >
          {children}
        </select>
        <ChevronDown
          className="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
          aria-hidden
        />
      </div>
    )
  },
)
Select.displayName = 'Select'

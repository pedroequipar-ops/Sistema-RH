import { type TextareaHTMLAttributes, forwardRef } from 'react'

import { cn } from '@/lib/cn'

type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
  invalid?: boolean
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, invalid, ...props }, ref) => {
    return (
      <textarea
        ref={ref}
        className={cn(
          'w-full rounded-lg border bg-white px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400',
          'focus:outline-none focus:ring-2 focus:ring-sapphire-400 focus:border-sapphire-400',
          invalid ? 'border-red-400' : 'border-slate-300',
          className,
        )}
        {...props}
      />
    )
  },
)
Textarea.displayName = 'Textarea'

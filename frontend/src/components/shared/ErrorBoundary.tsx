import { AlertTriangle } from 'lucide-react'
import { Component, type ReactNode } from 'react'

import { Button } from '@/components/ui/Button'

type Props = { children: ReactNode }
type State = { hasError: boolean }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-svh flex-col items-center justify-center gap-4 bg-slate-50 px-4 text-center">
          <span className="flex h-12 w-12 items-center justify-center rounded-full bg-red-50">
            <AlertTriangle className="h-6 w-6 text-red-600" aria-hidden />
          </span>
          <div>
            <h1 className="text-lg font-semibold text-slate-900">Algo deu errado</h1>
            <p className="mt-1 text-sm text-slate-500">
              Ocorreu um erro inesperado nesta tela. Tente recarregar a página.
            </p>
          </div>
          <Button onClick={() => window.location.assign('/')}>Voltar ao início</Button>
        </div>
      )
    }

    return this.props.children
  }
}

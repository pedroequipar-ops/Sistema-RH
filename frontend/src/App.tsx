import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { AppShell } from '@/components/layout/AppShell'
import { AuthProvider } from '@/context/AuthContext'
import { FuncionarioDetailPage } from '@/pages/admissao/FuncionarioDetailPage'
import { FuncionariosListPage } from '@/pages/admissao/FuncionariosListPage'
import { CandidatoDetailPage } from '@/pages/candidatos/CandidatoDetailPage'
import { CandidatosListPage } from '@/pages/candidatos/CandidatosListPage'
import { ComunicacoesPage } from '@/pages/comunicacoes/ComunicacoesPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { LoginPage } from '@/pages/LoginPage'
import { PerfisPage } from '@/pages/perfis/PerfisPage'
import { ProcessoDetailPage } from '@/pages/processos/ProcessoDetailPage'
import { ProcessosKanbanPage } from '@/pages/processos/ProcessosKanbanPage'
import { RelatoriosPage } from '@/pages/relatorios/RelatoriosPage'
import { UsuariosPage } from '@/pages/usuarios/UsuariosPage'
import { VagaDetailPage } from '@/pages/vagas/VagaDetailPage'
import { VagaFormPage } from '@/pages/vagas/VagaFormPage'
import { VagasListPage } from '@/pages/vagas/VagasListPage'
import { ProtectedRoute } from '@/routes/ProtectedRoute'
import { RequirePermission } from '@/routes/RequirePermission'
import { RequireRole } from '@/routes/RequireRole'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<ProtectedRoute />}>
              <Route element={<AppShell />}>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/vagas" element={<VagasListPage />} />
                <Route
                  path="/vagas/nova"
                  element={
                    <RequirePermission functionSlug="vagas" action="create" redirectTo="/vagas">
                      <VagaFormPage />
                    </RequirePermission>
                  }
                />
                <Route path="/vagas/:id" element={<VagaDetailPage />} />
                <Route path="/candidatos" element={<CandidatosListPage />} />
                <Route path="/candidatos/:id" element={<CandidatoDetailPage />} />
                <Route path="/processos-seletivos" element={<ProcessosKanbanPage />} />
                <Route path="/processos-seletivos/:id" element={<ProcessoDetailPage />} />
                <Route path="/comunicacoes" element={<ComunicacoesPage />} />
                <Route path="/relatorios" element={<RelatoriosPage />} />
                <Route path="/admissao" element={<FuncionariosListPage />} />
                <Route path="/admissao/:id" element={<FuncionarioDetailPage />} />
                <Route
                  path="/usuarios"
                  element={
                    <RequireRole roles={['gestor']} redirectTo="/">
                      <UsuariosPage />
                    </RequireRole>
                  }
                />
                <Route
                  path="/perfis-acesso"
                  element={
                    <RequireRole roles={['gestor']} redirectTo="/">
                      <PerfisPage />
                    </RequireRole>
                  }
                />
              </Route>
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

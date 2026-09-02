import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { AppShell } from '@/components/layout/AppShell'
import { AuthProvider } from '@/context/AuthContext'
import { DashboardPage } from '@/pages/DashboardPage'
import { LoginPage } from '@/pages/LoginPage'
import { PlaceholderPage } from '@/pages/PlaceholderPage'
import { ProtectedRoute } from '@/routes/ProtectedRoute'

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
                <Route path="/vagas" element={<PlaceholderPage title="Vagas" />} />
                <Route path="/candidatos" element={<PlaceholderPage title="Candidatos" />} />
                <Route
                  path="/processos-seletivos"
                  element={<PlaceholderPage title="Processos seletivos" />}
                />
                <Route path="/comunicacoes" element={<PlaceholderPage title="Comunicações" />} />
                <Route path="/relatorios" element={<PlaceholderPage title="Relatórios" />} />
                <Route path="/admissao" element={<PlaceholderPage title="Admissão" />} />
              </Route>
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

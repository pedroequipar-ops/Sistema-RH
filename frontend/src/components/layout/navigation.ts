import {
  BarChart3,
  Briefcase,
  KanbanSquare,
  LayoutDashboard,
  Mail,
  ShieldCheck,
  UserCheck,
  UserCog,
  Users,
  type LucideIcon,
} from 'lucide-react'

import type { Role } from '@/types/auth'

export type NavItem = {
  label: string
  to: string
  icon: LucideIcon
  functionSlug: string | null
  rolesOnly?: Role[]
}

export const NAV_ITEMS: NavItem[] = [
  { label: 'Painel', to: '/', icon: LayoutDashboard, functionSlug: null },
  { label: 'Vagas', to: '/vagas', icon: Briefcase, functionSlug: 'vagas' },
  { label: 'Candidatos', to: '/candidatos', icon: Users, functionSlug: 'candidatos' },
  {
    label: 'Processos seletivos',
    to: '/processos-seletivos',
    icon: KanbanSquare,
    functionSlug: 'processos-seletivos',
  },
  { label: 'Comunicações', to: '/comunicacoes', icon: Mail, functionSlug: 'comunicacoes' },
  { label: 'Relatórios', to: '/relatorios', icon: BarChart3, functionSlug: 'relatorios' },
  { label: 'Admissão', to: '/admissao', icon: UserCheck, functionSlug: 'admissao' },
  {
    label: 'Usuários',
    to: '/usuarios',
    icon: UserCog,
    functionSlug: null,
    rolesOnly: ['gestor'],
  },
  {
    label: 'Perfis de acesso',
    to: '/perfis-acesso',
    icon: ShieldCheck,
    functionSlug: null,
    rolesOnly: ['gestor'],
  },
]

# Sistema RH — Frontend

Frontend do sistema de recrutamento e seleção: React 19 + TypeScript + Vite + Tailwind v4.

## Stack

- React Router para navegação, React Query para dados remotos
- React Hook Form + Zod para formulários
- Axios com injeção automática de `Authorization` e `X-Company-ID`, e refresh de token em respostas 401
- lucide-react para ícones (sem emoji em nenhum lugar da UI)

## Rodando localmente

```bash
npm install
npm run dev
```

Requer o backend (`../`) rodando via `docker compose up` e a variável `VITE_API_URL` (ver `.env.example`) apontando para ele.

## Scripts

- `npm run dev` — servidor de desenvolvimento
- `npm run build` — type-check (`tsc -b`) + build de produção
- `npm run lint` — lint (oxlint)

## Estrutura

Um diretório por módulo de domínio em `src/pages/` (vagas, candidatos, processos, comunicacoes, relatorios, admissao), espelhando os apps do backend. `src/api/` e `src/hooks/` seguem a mesma divisão. Componentes de UI genéricos em `src/components/ui/`, layout em `src/components/layout/`.

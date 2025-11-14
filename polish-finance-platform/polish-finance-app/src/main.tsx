import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from 'next-themes'
import { Toaster } from 'sonner'
import { ErrorBoundary } from './components/ErrorBoundary.tsx'
import './index.css'
import App from './App.tsx'

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 2,
      staleTime: 30000,
    },
  },
})

const root = createRoot(document.getElementById('root')!);

root.render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      {/* @ts-ignore - next-themes ThemeProvider children prop type issue */}
      <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
        <ErrorBoundary>
          <App />
          <Toaster 
            position="top-right"
            richColors
            closeButton
            toastOptions={{
              style: {
                background: '#1E2433',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: '#F8FAFC',
              },
            }}
          />
        </ErrorBoundary>
      </ThemeProvider>
    </QueryClientProvider>
  </StrictMode>
)

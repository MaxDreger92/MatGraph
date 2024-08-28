import React, { useState } from "react"
//import ReactDOM from 'react-dom'
import { createRoot } from "react-dom/client"
import "./index.css"
import App from "./App"
import reportWebVitals from "./reportWebVitals"
import toast from "react-hot-toast"
import { BrowserRouter, HashRouter } from "react-router-dom"
import { QueryCache, QueryClient, QueryClientProvider } from "react-query"
import { MantineProvider, ColorSchemeProvider, ColorScheme } from "@mantine/core"

const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError(error, query) {
      if (query.state.data !== undefined) {
        if (error instanceof Error) {
          toast.error(`Something went wrong: ${error.message}`)
        }
      }
    },
  }),
})

const container = document.getElementById("root")
const root = createRoot(container as HTMLElement)

const ThemeProvider = () => {
  const [colorScheme, setColorScheme] = useState<ColorScheme>('dark')
  const toggleColorScheme = (value?: ColorScheme) =>
    setColorScheme(value || (colorScheme === 'dark' ? 'light' : 'dark'))

  return (
    <ColorSchemeProvider colorScheme={colorScheme} toggleColorScheme={toggleColorScheme}>
      <MantineProvider
        theme={{ colorScheme }}
        withGlobalStyles
        withNormalizeCSS
      >
        <App />
      </MantineProvider>
    </ColorSchemeProvider>
  )
}

root.render(
  // <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ThemeProvider />
      </BrowserRouter>
    </QueryClientProvider>
  // </React.StrictMode>
)

reportWebVitals()

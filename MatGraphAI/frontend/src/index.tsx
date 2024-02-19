import React from "react"
//import ReactDOM from 'react-dom'
import { createRoot } from "react-dom/client"
import "./index.css"
import App from "./App"
import reportWebVitals from "./reportWebVitals"
import toast from "react-hot-toast"
import { BrowserRouter, HashRouter } from "react-router-dom"
import { QueryCache, QueryClient, QueryClientProvider } from "react-query"
import { MantineProvider } from "@mantine/core"

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
// @ts-ignore
const root = createRoot(container)

// console.log(process.env.REACT_APP_PUBLIC_URL)

root.render(
  // <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <HashRouter>
        <MantineProvider
          theme={{ colorScheme: "dark" }}
          withGlobalStyles
          withNormalizeCSS
        > 
          <App />
        </MantineProvider>
      </HashRouter>
    </QueryClientProvider>
  // </React.StrictMode>
)

//########## React 17 ###########
// ReactDOM.render(
//   <React.StrictMode>
//     <QueryClientProvider client={queryClient}>
//       <BrowserRouter>
//         <App />
//       </BrowserRouter>
//     </QueryClientProvider>
//   </React.StrictMode>,
//   document.getElementById('root')
// )

reportWebVitals()

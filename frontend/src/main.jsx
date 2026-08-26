import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './viewportScale.js'
import './visualMirror.js'
import HomeShell from './HomeShell.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <HomeShell />
  </StrictMode>,
)

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './viewportScale.js'
import './safeVisualBridge.css'
import './safeVisualBridge.js'
import HomeShell from './HomeShell.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <HomeShell />
  </StrictMode>,
)

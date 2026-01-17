import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import Recommend from './pages/Recommend'
import Exercises from './pages/Exercises'
import Profile from './pages/Profile'
import './App.css'

function App() {
  const [darkMode, setDarkMode] = useState(true)

  return (
    <Router>
      <div className={`app ${darkMode ? 'dark' : 'light'}`}>
        <nav className="navbar">
          <div className="nav-brand">
            <span className="logo">💪</span>
            <span className="brand-name">GymRec</span>
          </div>
          <div className="nav-links">
            <Link to="/" className="nav-link">Home</Link>
            <Link to="/recommend" className="nav-link">Get Recommendations</Link>
            <Link to="/exercises" className="nav-link">Browse Exercises</Link>
            <Link to="/profile" className="nav-link">Profile</Link>
          </div>
          <button 
            className="theme-toggle"
            onClick={() => setDarkMode(!darkMode)}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/recommend" element={<Recommend />} />
            <Route path="/exercises" element={<Exercises />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </main>

        <footer className="footer">
          <p>© 2024 GymRec - Gym Exercise Recommendation System</p>
        </footer>
      </div>
    </Router>
  )
}

export default App

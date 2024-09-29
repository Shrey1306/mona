import './App.css';
import React from 'react';
import LoginPage from './Login/LoginPage';
import Dashboard from './Dashboard/Dashboard';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';

function AppWithLayout() {
  const location = useLocation(); // Use location here for keying transitions

  return (
    <AnimatePresence mode='wait'>
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<LoginPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </AnimatePresence>
  );
}

function App() {
  return (
    <Router>
      <AppWithLayout /> {/* Wrap the Routes and AnimatePresence in a component that has access to the location */}
    </Router>
  );
}

export default App;

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';  // Assuming you have this component
import ProcessingPage from './components/ProcessingPage';  // Assuming you have this component
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/processing" element={<ProcessingPage />} />
      </Routes>
    </Router>
  );
}

export default App;


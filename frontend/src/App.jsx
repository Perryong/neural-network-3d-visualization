import React, { useState } from 'react';
import TabNavigation from './components/TabNavigation';
import VisualizationPage from './components/VisualizationPage';
import TrainingPage from './components/TrainingPage';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('visualization');

  return (
    <div className="app">
      <TabNavigation activeTab={activeTab} setActiveTab={setActiveTab} />
      {activeTab === 'visualization' && <VisualizationPage />}
      {activeTab === 'training' && <TrainingPage />}
    </div>
  );
}

export default App;


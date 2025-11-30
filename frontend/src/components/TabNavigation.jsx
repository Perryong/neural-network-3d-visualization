import React from 'react';
import './TabNavigation.css';

function TabNavigation({ activeTab, setActiveTab }) {
  return (
    <div className="tab-navigation">
      <button
        className={`tab-button ${activeTab === 'visualization' ? 'active' : ''}`}
        onClick={() => setActiveTab('visualization')}
      >
        Visualization
      </button>
      <button
        className={`tab-button ${activeTab === 'training' ? 'active' : ''}`}
        onClick={() => setActiveTab('training')}
      >
        Training
      </button>
    </div>
  );
}

export default TabNavigation;


import React, { useState } from 'react';
import './TrainingPage.css';

function TrainingPage() {
  const [formData, setFormData] = useState({
    epochs: 5,
    batchSize: 128,
    hiddenDims: '128, 64',
    learningRate: 0.001,
    device: 'auto',
    forceTrain: false,
  });
  const [isTraining, setIsTraining] = useState(false);
  const [trainingStatus, setTrainingStatus] = useState(null);
  const [trainingOutput, setTrainingOutput] = useState('');

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsTraining(true);
    setTrainingStatus(null);
    setTrainingOutput('Starting training...\n');

    // Parse hidden dimensions
    const hiddenDims = formData.hiddenDims
      .split(',')
      .map((s) => parseInt(s.trim()))
      .filter((n) => !isNaN(n) && n > 0);

    if (hiddenDims.length === 0) {
      alert("Please enter valid hidden layer dimensions (e.g., '128, 64')");
      setIsTraining(false);
      return;
    }

    try {
      const response = await fetch('/api/v1/training/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          epochs: parseInt(formData.epochs),
          batch_size: parseInt(formData.batchSize),
          hidden_dims: hiddenDims,
          lr: parseFloat(formData.learningRate),
          device: formData.device === 'auto' ? null : formData.device,
          force: formData.forceTrain,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setTrainingOutput((prev) => prev + `\n${data.message || 'Training completed successfully!'}\n`);
        if (data.data && data.data.location) {
          setTrainingOutput((prev) => prev + `\nWeights saved to: ${data.data.location}\n`);
        }
        setTrainingStatus('success');
      } else {
        setTrainingOutput((prev) => prev + `\nError: ${data.message || 'Training failed'}\n`);
        if (data.data && data.data.stderr) {
          setTrainingOutput((prev) => prev + `\n${data.data.stderr}\n`);
        }
        setTrainingStatus('error');
      }
    } catch (error) {
      setTrainingOutput((prev) => prev + `\nError: ${error.message}\n`);
      setTrainingStatus('error');
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <div className="training-container">
      <h2>Model Training</h2>
      <p className="training-description">
        Configure hyperparameters and train a new model. Training may take several minutes.
      </p>

      <form onSubmit={handleSubmit} className="training-form">
        <div className="form-group">
          <label htmlFor="epochs">Epochs</label>
          <input
            type="number"
            id="epochs"
            name="epochs"
            min="1"
            max="50"
            value={formData.epochs}
            onChange={handleInputChange}
            required
          />
          <span className="form-hint">Number of training epochs (default: 5)</span>
        </div>

        <div className="form-group">
          <label htmlFor="batchSize">Batch Size</label>
          <input
            type="number"
            id="batchSize"
            name="batchSize"
            min="1"
            max="512"
            value={formData.batchSize}
            onChange={handleInputChange}
            required
          />
          <span className="form-hint">Mini-batch size for training (default: 128)</span>
        </div>

        <div className="form-group">
          <label htmlFor="hiddenDims">Hidden Layer Dimensions</label>
          <input
            type="text"
            id="hiddenDims"
            name="hiddenDims"
            value={formData.hiddenDims}
            onChange={handleInputChange}
            required
            pattern="^\d+(\s*,\s*\d+)*$"
            placeholder="128, 64"
          />
          <span className="form-hint">
            Comma-separated list of hidden layer sizes (default: 128, 64)
          </span>
        </div>

        <div className="form-group">
          <label htmlFor="learningRate">Learning Rate</label>
          <input
            type="number"
            id="learningRate"
            name="learningRate"
            min="0.0001"
            max="1"
            step="0.0001"
            value={formData.learningRate}
            onChange={handleInputChange}
            required
          />
          <span className="form-hint">Learning rate for Adam optimizer (default: 0.001)</span>
        </div>

        <div className="form-group">
          <label htmlFor="device">Device</label>
          <select id="device" name="device" value={formData.device} onChange={handleInputChange}>
            <option value="auto">Auto (Best Available)</option>
            <option value="mps">MPS (Apple Silicon)</option>
            <option value="cuda">CUDA (NVIDIA GPU)</option>
            <option value="cpu">CPU</option>
          </select>
          <span className="form-hint">Device to use for training</span>
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              id="forceTrain"
              name="forceTrain"
              checked={formData.forceTrain}
              onChange={handleInputChange}
            />
            Force Training (retrain even if weights exist)
          </label>
        </div>

        <button type="submit" className="training-button" disabled={isTraining}>
          {isTraining ? 'Training...' : 'Start Training'}
        </button>
      </form>

      {(trainingStatus || trainingOutput) && (
        <div className="training-status">
          <h3>Training Status</h3>
          <div className={`training-output ${trainingStatus || ''}`}>{trainingOutput}</div>
        </div>
      )}
    </div>
  );
}

export default TrainingPage;


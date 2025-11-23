# Neural Network Visualization

> An interactive 3D visualization tool for understanding how neural networks process information in real-time. Visualize a Multi-Layer Perceptron (MLP) trained on MNIST digit classification with live activations as you draw.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-1.9+-orange.svg)](https://pytorch.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ Features

- 🎨 **Interactive 3D Visualization** - Explore neural network architecture in real-time with Three.js
- 📊 **Training Timeline** - Watch the network learn through 26 training snapshots
- 🖊️ **Digit Drawing** - Draw digits on a 28×28 grid and see instant predictions
- 📈 **Real-Time Activations** - See how signals propagate through layers as you draw
- 🎯 **MNIST Integration** - Load actual test samples with one click
- 🚀 **Zero Configuration** - Automatically handles training and setup
- 📱 **Responsive Design** - Works on desktop and mobile devices
- 🎓 **Educational** - Perfect for understanding neural network internals

---

## 📸 Screenshots

> **Add screenshots/GIFs here to showcase:**
> - 3D neural network visualization
> - Real-time activation propagation
> - Training timeline interface
> - Digit drawing interface

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **PyTorch** (installed automatically with pip)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)
- **Git** (for cloning)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/neural-network-visualization.git
cd neural-network-visualization

# Install Python dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

**Alternative:** Run the backend launcher directly:
```bash
python -m backend.launcher
```

The application will automatically:
1. ✅ Check if trained weights exist
2. 🎓 Train the model if needed (first run only, ~5-10 minutes)
3. 📦 Prepare MNIST test assets if needed
4. 🌐 Start web server on http://localhost:8000
5. 🌍 Open browser automatically

**First run will take longer** as it needs to download MNIST dataset and train the model.

---

## 📖 Usage

### Basic Usage

```bash
# Start the application with default settings
python main.py
```

### Command-Line Options

```bash
# Use a custom port
python main.py --port 8080

# Force retrain the model (even if weights exist)
python main.py --force-train

# Skip training (use existing weights)
python main.py --no-train

# Skip MNIST asset preparation
python main.py --no-mnist-prep

# Don't open browser automatically
python main.py --no-browser

# Prepare MNIST assets manually
python main.py --prepare-mnist

# Force prepare MNIST assets (overwrite existing)
python main.py --force-prepare-mnist

# Get help
python main.py --help
```

### Using the Visualization

1. **Draw a Digit**: Click and drag on the 28×28 grid (top left). Right-click to erase.
2. **Load MNIST Sample**: Click digit buttons (0-9) to load test images from the MNIST dataset.
3. **Navigate 3D View**: 
   - **Rotate**: Left mouse button + drag
   - **Pan**: Right mouse button + drag
   - **Zoom**: Scroll wheel
   - **Touch Controls**: One finger drag to rotate, two fingers to pan, pinch to zoom
4. **Explore Timeline**: Use the slider at the bottom to view network at different training stages.
5. **Inspect Neurons**: Click on neurons to see detailed information about weights, activations, and connections.
6. **Adjust Settings**: Click ⚙️ button for advanced settings (connection display, brush size, etc.).

---

## 🏗️ Architecture Overview

The application consists of **three main components**:

1. **Backend (Python/Flask)** - REST API server for training, asset management, and model info
2. **Frontend (JavaScript/Three.js)** - Interactive 3D visualization in the browser
3. **Training (Python/PyTorch)** - Neural network training and weight export

```
┌─────────────────┐
│   main.py       │  ← Entry point: Starts Flask server, runs training if needed
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│Backend│ │Frontend │
│ Flask │ │Three.js │
│  API  │ │  3D UI  │
└───────┘ └─────────┘
    │
┌───▼──────┐
│ Training │
│ PyTorch  │
└──────────┘
```

---

## 📁 Project Structure

```
neural-network-visualization/
├── main.py                    # Main entry point (compatibility wrapper)
├── requirements.txt            # Python dependencies
├── README.md                  # This file
├── LICENSE                    # License file
├── .gitignore                 # Git ignore rules
├── fix_timeline.py           # Utility to fix timeline references
│
├── backend/
│   ├── __init__.py
│   ├── server.py              # Flask application and server setup
│   ├── launcher.py            # Application launcher with CLI
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py          # REST API route handlers
│   │   └── models.py          # API response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── training_service.py # Training orchestration
│   │   └── asset_service.py    # MNIST asset management
│   ├── training/
│   │   └── mlp_train.py      # Neural network training script
│   ├── tools/
│   │   └── mnist_assets/
│   │       └── prepare_mnist_test_assets.py  # Prepares MNIST test data
│   └── data/
│       └── MNIST/            # MNIST dataset (downloaded automatically)
│
└── frontend/
    ├── index.html            # Frontend HTML entry point
    ├── assets/
    │   ├── main.js           # All frontend JavaScript
    │   ├── main.css          # Styling
    │   └── data/             # MNIST test samples (binary format)
    └── exports/
        ├── mlp_weights.json  # Network definition + timeline manifest
        └── mlp_weights/      # Training snapshots (26 JSON files)
```

---

## 🔄 How It Works

### Training Phase (Backend)

The backend trains a Multi-Layer Perceptron (MLP) on the MNIST dataset:

```
MNIST Dataset (60,000 training images)
    ↓
PyTorch DataLoader (batch size: 128)
    ↓
SmallMLP Model Training
    ├── Forward Pass: Input → Hidden Layers → Output
    ├── Loss Calculation: Cross-Entropy Loss
    ├── Backward Pass: Gradient Computation
    └── Weight Update: Adam Optimizer (lr=0.001)
    ↓
Timeline Snapshots (captured at milestones)
    ├── 000_initial.json (random weights)
    ├── 001_approx-50.json (after ~50 images)
    ├── 002_approx-120.json
    ├── ...
    └── 025_dataset-12-5x.json (after 12.5× dataset)
    ↓
Export to JSON (Base64-encoded float16)
    └── mlp_weights.json (manifest + metadata)
```

### Visualization Phase (Frontend)

The frontend runs real-time inference in the browser:

```
User draws digit on 28×28 grid
    ↓
DigitSketchPad.getPixels() → Float32Array[784]
    ↓
FeedForwardModel.propagate(input)
    ├── Normalize: (pixel - 0.1307) / 0.3081
    ├── Layer 1: 784 → 128 (ReLU activation)
    ├── Layer 2: 128 → 64 (ReLU activation)
    └── Layer 3: 64 → 10 (Linear output)
    ↓
NeuralVisualizer.update(activations)
    ├── Update neuron colors (based on activation values)
    ├── Update connection colors (based on weight strength)
    └── Render 3D scene (Three.js)
    ↓
ProbabilityPanel.update(probabilities)
    └── Display bar chart (0-9 digit probabilities)
```

---

## 🧠 Neural Network Architecture

### Default Architecture

```
Input Layer:     784 neurons (28×28 pixel grid)
  ↓
Dense Layer 1:   128 neurons (ReLU activation)
  ↓
Dense Layer 2:   64 neurons (ReLU activation)
  ↓
Output Layer:    10 neurons (Linear → Softmax)
```

**Total Parameters**: ~109,000 weights + biases

### Customizing Architecture

```bash
# Train with different hidden layer sizes
python backend/training/mlp_train.py --hidden-dims 256 128 64

# Adjust training parameters
python backend/training/mlp_train.py --epochs 10 --batch-size 64 --lr 0.001
```

---

## 🔧 Technical Details

### Weight Format
- **Encoding**: Base64-encoded float16 arrays
- **Size**: 2 bytes per weight (50% smaller than float32)
- **Decoding**: Custom JavaScript `float16ToFloat32()` function

### Performance Optimizations
- **Connection Limiting**: Only shows top N strongest connections per neuron
- **Connection Thresholding**: Filters out weak connections
- **Instanced Rendering**: Reuses geometry for similar neurons
- **RequestAnimationFrame**: Smooth 60fps updates

### 3D Rendering (Three.js)
- **Neurons**: Sphere geometries (hidden layers) and box geometries (input layer)
- **Connections**: Cylinder geometries colored by weight strength
- **Color Gradients**: Blue (low/negative) → Orange/Red (high positive)
- **Controls**: OrbitControls for camera interaction

---

## 🎓 Training Timeline Feature

Explore how the network learns over time with 26 training snapshots:
- **Initial Weights**: Random initialization (accuracy: ~10%)
- **Early Training**: After ~50, 120, 250 images...
- **Mid Training**: After ~1k, 2k, 3.5k images...
- **Late Training**: After 1×, 1.5×, 2× dataset passes...
- **Final Model**: After 12.5× dataset (accuracy: ~98%)

---

## 🔌 REST API

The backend provides a REST API for programmatic access to training, assets, and model information.

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### Health Check
```http
GET /api/v1/health
```
Returns API health status.

**Response:**
```json
{
  "success": true,
  "message": "API is healthy"
}
```

#### Model Information
```http
GET /api/v1/model/info
```
Get model metadata and weights information.

**Response:**
```json
{
  "success": true,
  "data": {
    "exists": true,
    "location": "path/to/mlp_weights.json",
    "architecture": [784, 128, 64, 10],
    "layers": 3,
    "timeline_entries": 26
  }
}
```

#### Start Training
```http
POST /api/v1/training/start
Content-Type: application/json

{
  "force": false
}
```
Start training job. Set `force: true` to retrain even if weights exist.

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Training completed successfully!",
    "location": "path/to/mlp_weights.json"
  }
}
```

#### Training Status
```http
GET /api/v1/training/status
```
Get current training status and model information.

#### Prepare MNIST Assets
```http
POST /api/v1/assets/prepare-mnist
Content-Type: application/json

{
  "force": false
}
```
Prepare MNIST test assets. Set `force: true` to regenerate even if assets exist.

#### MNIST Asset Status
```http
GET /api/v1/assets/mnist-status
```
Get status of MNIST assets.

**Response:**
```json
{
  "success": true,
  "data": {
    "exists": true,
    "num_samples": 10000,
    "image_shape": [28, 28]
  }
}
```

#### Validate Timeline
```http
GET /api/v1/timeline/validate?fix=true
```
Validate timeline entries. Add `?fix=true` to automatically fix missing entries.

#### Fix Timeline
```http
POST /api/v1/timeline/fix
```
Fix timeline issues by removing invalid entries.

### Example Usage

```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Get model info
curl http://localhost:8000/api/v1/model/info

# Start training
curl -X POST http://localhost:8000/api/v1/training/start \
  -H "Content-Type: application/json" \
  -d '{"force": false}'

# Prepare MNIST assets
curl -X POST http://localhost:8000/api/v1/assets/prepare-mnist \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

---

## 🐛 Troubleshooting

**Problem**: Training takes too long
- **Solution**: Use GPU acceleration or use existing weights: `python main.py --no-train`

**Problem**: Port already in use
- **Solution**: Use `--port` flag: `python main.py --port 8080`

**Problem**: Timeline snapshots missing (404 errors)
- **Solution**: Run `python fix_timeline.py` to clean up timeline references

**Problem**: MNIST assets not loading
- **Solution**: Run `python main.py --prepare-mnist` to regenerate assets

**Problem**: Browser doesn't open automatically
- **Solution**: Manually navigate to http://localhost:8000

---

## 📊 Requirements

### Python Dependencies
All dependencies are listed in `requirements.txt`:
- `torch>=1.9.0` - PyTorch for neural network training
- `torchvision>=0.10.0` - MNIST dataset loading
- `numpy>=1.19.0` - Numerical operations
- `Flask>=2.0.0` - Web framework for REST API
- `flask-cors>=3.0.0` - CORS support for API

Install with:
```bash
pip install -r requirements.txt
```

### Browser Requirements
- Modern browser with WebGL support (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- ES6+ support

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **MNIST Dataset** - Yann LeCun, Corinna Cortes, and Christopher Burges
- **Three.js** - 3D graphics library for web
- **PyTorch** - Deep learning framework
- **Original Implementation** - Based on work by DFin

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/neural-network-visualization/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/neural-network-visualization/discussions)

---

**Made with ❤️ for learning and education**

If you find this project helpful, please ⭐ star it and share with others!

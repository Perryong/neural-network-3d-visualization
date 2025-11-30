// Re-export visualization utilities and classes
// This file will import from the existing main.js bundle
// For now, we'll load it as a module

export const VISUALIZER_CONFIG = {
  weightUrl: "./exports/mlp_weights.json",
  maxConnectionsPerNeuron: 24,
  layerSpacing: 5.5,
  inputSpacing: 0.24,
  hiddenSpacing: 0.95,
  inputNodeSize: 0.18,
  hiddenNodeRadius: 0.22,
  connectionRadius: 0.005,
  connectionWeightThreshold: 0,
  showFpsOverlay: true,
  brush: {
    drawRadius: 1.4,
    eraseRadius: 2.5,
    drawStrength: 0.95,
    eraseStrength: 0.95,
    softness: 0.3,
  },
};

export const MNIST_SAMPLE_MANIFEST_URL = "./assets/data/mnist-test-manifest.json";


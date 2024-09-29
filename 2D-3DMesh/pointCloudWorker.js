// src/workers/pointCloudWorker.js

export function generatePointCloud({ imageData, width, height, skip }) {
  const points = [];
  for (let y = 0; y < height; y += skip) {
    for (let x = 0; x < width; x += skip) {
      const idx = (y * width + x) * 4;
      const r = imageData[idx] / 255;
      const g = imageData[idx + 1] / 255;
      const b = imageData[idx + 2] / 255;
      const brightness = (r + g + b) / 3;

      const px = (x / width) * 2 - 1;
      const py = -(y / height) * 2 + 1;
      const pz = -brightness * 0.5;

      points.push({ position: [px, py, pz], color: [r, g, b] });
    }
  }

  postMessage({ points });
}

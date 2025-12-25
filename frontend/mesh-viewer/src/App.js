import React, { useRef, useState, useEffect, useCallback } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const PIXEL_SAMPLE_RATE = 2;

const TOOL_COLORS = {
  scalpel: 0xff0000,
  cautery: 0xffff00,
  laser: 0x00ff00,
};

function App() {
  const [stage, setStage] = useState('idle');
  const [capturedImages, setCapturedImages] = useState([]);
  const [activeImageIndex, setActiveImageIndex] = useState(0);
  const [isAnnotating, setIsAnnotating] = useState(true);
  const [annotations, setAnnotations] = useState([]);
  const [selectedTool, setSelectedTool] = useState('scalpel');
  const [toolWidth, setToolWidth] = useState(1);

  const videoRef = useRef(null);
  const containerRef = useRef(null);
  const canvas2DRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const pointCloudRef = useRef(null);
  const controlsRef = useRef(null);
  const raycaster = useRef(new THREE.Raycaster());
  const mouse = useRef(new THREE.Vector2());
  const storedAnnotations = useRef([]);
  const activeAnnotation = useRef(null);
  const isDrawing = useRef(false);

  const getToolMaterial = useCallback((tool, width) => {
    return new THREE.LineBasicMaterial({
      color: TOOL_COLORS[tool],
      linewidth: width,
    });
  }, []);

  useEffect(() => {
    if (stage === 'scanning') {
      startCamera();
    } else if (stage === 'processing') {
      initScene();
      generatePointCloud();
    }
  }, [stage]);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
    } catch (err) {
      console.error('Camera access error:', err);
    }
  };

  const captureFrame = useCallback(() => {
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    setCapturedImages((prev) => [...prev, canvas.toDataURL('image/jpeg')]);
  }, []);

  const initScene = () => {
    const container = containerRef.current;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      75,
      container.clientWidth / container.clientHeight,
      0.1,
      1000
    );
    const renderer = new THREE.WebGLRenderer({ antialias: true });

    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);
    camera.position.z = 500;

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    controls.enableZoom = true;
    controls.enabled = !isAnnotating;
    controlsRef.current = controls;

    const geometry = new THREE.BufferGeometry();
    const material = new THREE.PointsMaterial({ size: 2, vertexColors: true });
    const pointCloud = new THREE.Points(geometry, material);
    scene.add(pointCloud);

    sceneRef.current = scene;
    cameraRef.current = camera;
    rendererRef.current = renderer;
    pointCloudRef.current = pointCloud;

    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    container.addEventListener('pointerdown', handlePointerDown);
    container.addEventListener('pointermove', handlePointerMove);
    container.addEventListener('pointerup', handlePointerUp);
    container.addEventListener('dblclick', toggleMode);
  };

  const generatePointCloud = async () => {
    const points = [];

    for (let imgIdx = 0; imgIdx < capturedImages.length; imgIdx++) {
      const img = await loadImage(capturedImages[imgIdx]);
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

      for (let y = 0; y < canvas.height; y += PIXEL_SAMPLE_RATE) {
        for (let x = 0; x < canvas.width; x += PIXEL_SAMPLE_RATE) {
          const i = (y * canvas.width + x) * 4;
          const r = imageData.data[i] / 255;
          const g = imageData.data[i + 1] / 255;
          const b = imageData.data[i + 2] / 255;
          const brightness = (r + g + b) / 3;
          const z = brightness * 50 + imgIdx * 20;

          points.push({
            position: [x - canvas.width / 2, -y + canvas.height / 2, z],
            color: [r, g, b],
          });
        }
      }
    }

    updatePointCloudGeometry(points);
  };

  const loadImage = (src) => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = src;
    });
  };

  const updatePointCloudGeometry = (points) => {
    const geometry = pointCloudRef.current.geometry;
    const positions = new Float32Array(points.length * 3);
    const colors = new Float32Array(points.length * 3);

    points.forEach((point, i) => {
      positions[i * 3] = point.position[0];
      positions[i * 3 + 1] = point.position[1];
      positions[i * 3 + 2] = point.position[2];
      colors[i * 3] = point.color[0];
      colors[i * 3 + 1] = point.color[1];
      colors[i * 3 + 2] = point.color[2];
    });

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.computeBoundingSphere();

    const center = geometry.boundingSphere.center;
    const radius = geometry.boundingSphere.radius;
    cameraRef.current.position.set(center.x, center.y, center.z + radius * 2);
    cameraRef.current.lookAt(center);
  };

  const toggleMode = useCallback(() => {
    setIsAnnotating((prev) => !prev);
    if (controlsRef.current) {
      controlsRef.current.enabled = isAnnotating;
    }
  }, [isAnnotating]);

  const handlePointerDown = (event) => {
    if (!isAnnotating) return;
    isDrawing.current = true;
    updateMousePosition(event);
    startNewAnnotation();
  };

  const handlePointerMove = (event) => {
    if (!isAnnotating || !isDrawing.current) return;
    updateMousePosition(event);
    extendAnnotation();
  };

  const handlePointerUp = () => {
    if (!isAnnotating) return;
    isDrawing.current = false;
    finalizeAnnotation();
  };

  const updateMousePosition = (event) => {
    const rect = containerRef.current.getBoundingClientRect();
    mouse.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  };

  const startNewAnnotation = () => {
    raycaster.current.setFromCamera(mouse.current, cameraRef.current);
    const hits = raycaster.current.intersectObject(pointCloudRef.current);

    if (hits.length > 0) {
      const point = hits[0].point;
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute(
        'position',
        new THREE.BufferAttribute(new Float32Array([point.x, point.y, point.z]), 3)
      );
      const line = new THREE.Line(geometry, getToolMaterial(selectedTool, toolWidth));
      sceneRef.current.add(line);
      activeAnnotation.current = line;
      logAnnotation(point);
    }
  };

  const extendAnnotation = () => {
    raycaster.current.setFromCamera(mouse.current, cameraRef.current);
    const hits = raycaster.current.intersectObject(pointCloudRef.current);

    if (hits.length > 0 && activeAnnotation.current) {
      const newPoint = hits[0].point;
      const positions = activeAnnotation.current.geometry.attributes.position;
      const newPositions = new Float32Array(positions.count * 3 + 3);
      newPositions.set(positions.array);
      newPositions[positions.count * 3] = newPoint.x;
      newPositions[positions.count * 3 + 1] = newPoint.y;
      newPositions[positions.count * 3 + 2] = newPoint.z;
      activeAnnotation.current.geometry.setAttribute(
        'position',
        new THREE.BufferAttribute(newPositions, 3)
      );
      logAnnotation(newPoint);
    }
  };

  const finalizeAnnotation = () => {
    if (activeAnnotation.current) {
      storedAnnotations.current.push(activeAnnotation.current);
      activeAnnotation.current = null;
    }
  };

  const logAnnotation = (point) => {
    const entry = `${selectedTool}: (${point.x.toFixed(2)}, ${point.y.toFixed(2)}, ${point.z.toFixed(2)})`;
    setAnnotations((prev) => [...prev, entry]);
  };

  const renderImageOn2D = useCallback(() => {
    if (!canvas2DRef.current || !capturedImages[activeImageIndex]) return;
    const ctx = canvas2DRef.current.getContext('2d');
    const img = new Image();
    img.onload = () => {
      canvas2DRef.current.width = img.width;
      canvas2DRef.current.height = img.height;
      ctx.clearRect(0, 0, img.width, img.height);
      ctx.drawImage(img, 0, 0);
    };
    img.src = capturedImages[activeImageIndex];
  }, [activeImageIndex, capturedImages]);

  useEffect(() => {
    if (stage === 'processing') {
      renderImageOn2D();
    }
  }, [stage, activeImageIndex, renderImageOn2D]);

  const styles = {
    button: { padding: '12px 24px', fontSize: '16px', margin: '8px', cursor: 'pointer' },
    text: { fontSize: '16px' },
  };

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <div style={{ width: '50%', padding: '20px' }}>
        <h1>Image Capture</h1>

        {stage === 'idle' && (
          <button style={styles.button} onClick={() => setStage('scanning')}>
            Start Scanning
          </button>
        )}

        {stage === 'scanning' && (
          <div>
            <video ref={videoRef} autoPlay style={{ width: '100%' }} />
            <button style={styles.button} onClick={captureFrame}>
              Capture Frame
            </button>
            <button
              style={styles.button}
              onClick={() => setStage('processing')}
              disabled={capturedImages.length < 3}
            >
              Process Images
            </button>
            <p style={styles.text}>Captured: {capturedImages.length} frames</p>
          </div>
        )}

        {stage === 'processing' && (
          <div>
            <canvas ref={canvas2DRef} style={{ width: '100%', height: 'auto' }} />
            <div>
              {capturedImages.map((_, idx) => (
                <button key={idx} style={styles.button} onClick={() => setActiveImageIndex(idx)}>
                  Frame {idx + 1}
                </button>
              ))}
            </div>
          </div>
        )}

        <div style={{ marginTop: '20px' }}>
          <h2>Annotation Log</h2>
          <ul style={styles.text}>
            {annotations.map((entry, idx) => (
              <li key={idx}>{entry}</li>
            ))}
          </ul>
        </div>
      </div>

      <div style={{ width: '50%', padding: '20px' }}>
        <h1>3D Reconstruction</h1>
        <div ref={containerRef} style={{ width: '100%', height: 'calc(100% - 200px)' }} />

        <div style={{ marginTop: '20px' }}>
          <h2>Tools</h2>
          <div style={styles.text}>
            <label>
              Tool:
              <select
                value={selectedTool}
                onChange={(e) => setSelectedTool(e.target.value)}
                style={styles.button}
              >
                <option value="scalpel">Scalpel</option>
                <option value="cautery">Cautery</option>
                <option value="laser">Laser</option>
              </select>
            </label>
          </div>
          <div style={styles.text}>
            <label>
              Width:
              <input
                type="range"
                min="1"
                max="10"
                value={toolWidth}
                onChange={(e) => setToolWidth(parseInt(e.target.value))}
                style={{ margin: '0 10px' }}
              />
              {toolWidth}
            </label>
          </div>
        </div>
        <p>Mode: {isAnnotating ? 'Annotate' : 'Rotate'}</p>
        <p style={{ color: '#666' }}>Double-click to toggle mode</p>
      </div>
    </div>
  );
}

export default App;

import React, { useRef, useState, useEffect, useCallback } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const SAMPLING_RATE = 2; // Increased sampling rate for better precision

const App = () => {
  const [scanningStage, setScanningStage] = useState('idle');
  const [scannedImages, setScannedImages] = useState([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isAnnotationMode, setIsAnnotationMode] = useState(true);
  const [annotationLog, setAnnotationLog] = useState([]);
  const [incisionType, setIncisionType] = useState('scalpel');
  const [incisionWidth, setIncisionWidth] = useState(1);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const imageCanvasRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const pointCloudRef = useRef(null);
  const raycasterRef = useRef(new THREE.Raycaster());
  const mouseRef = useRef(new THREE.Vector2());
  const controlsRef = useRef(null);
  const annotationsRef = useRef([]);
  const currentAnnotationRef = useRef(null);
  const isDrawingRef = useRef(false);

  const annotationMaterials = {
    scalpel: new THREE.LineBasicMaterial({ color: 0xff0000, linewidth: incisionWidth }),
    cautery: new THREE.LineBasicMaterial({ color: 0xffff00, linewidth: incisionWidth }),
    laser: new THREE.LineBasicMaterial({ color: 0x00ff00, linewidth: incisionWidth })
  };

  useEffect(() => {
    if (scanningStage === 'scanning') {
      startVideoStream();
    } else if (scanningStage === 'processing') {
      processScannedImages();
    }
  }, [scanningStage]);

  const startVideoStream = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
    } catch (err) {
      console.error("Error accessing the camera", err);
    }
  };

  const captureImage = useCallback(() => {
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    setScannedImages(prev => [...prev, canvas.toDataURL('image/jpeg')]);
  }, []);

  const processScannedImages = useCallback(async () => {
    initThreeJS();
    try {
      const pointCloudData = await generatePointCloudFromImages(scannedImages);
      updatePointCloud(pointCloudData);
    } catch (error) {
      console.error("Error processing images:", error);
    }
  }, [scannedImages]);

  const initThreeJS = () => {
    const container = canvasRef.current;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });

    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    camera.position.z = 500;

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    controls.enableZoom = true;
    controls.enabled = !isAnnotationMode;
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
      controls.update(); // Always update controls
      renderer.render(scene, camera);
    };
    animate();

    container.addEventListener('pointerdown', onPointerDown);
    container.addEventListener('pointermove', onPointerMove);
    container.addEventListener('pointerup', onPointerUp);
    container.addEventListener('dblclick', toggleMode);
  };
  const generatePointCloudFromImages = async (images) => {
    const points = [];
    for (let imageIndex = 0; imageIndex < images.length; imageIndex++) {
      const dataUrl = images[imageIndex];
      const img = await loadImage(dataUrl);
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0, img.width, img.height);
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      
      for (let y = 0; y < canvas.height; y += SAMPLING_RATE) {
        for (let x = 0; x < canvas.width; x += SAMPLING_RATE) {
          const i = (y * canvas.width + x) * 4;
          const r = imageData.data[i] / 255;
          const g = imageData.data[i + 1] / 255;
          const b = imageData.data[i + 2] / 255;
          const intensity = (r + g + b) / 3;

          const z = intensity * 50 + imageIndex * 20;

          points.push({
            position: [x - canvas.width / 2, -y + canvas.height / 2, z],
            color: [r, g, b],
            imageIndex,
            imageX: x,
            imageY: y
          });
        }
      }
    }
    return points;
  };

  const loadImage = (src) => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = src;
    });
  };

  const updatePointCloud = (pointCloudData) => {
    const geometry = pointCloudRef.current.geometry;
    const positions = new Float32Array(pointCloudData.length * 3);
    const colors = new Float32Array(pointCloudData.length * 3);

    pointCloudData.forEach((point, i) => {
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
    cameraRef.current.position.set(center.x, center.y, center.z + geometry.boundingSphere.radius * 2);
    cameraRef.current.lookAt(center);
  };

  const toggleMode = useCallback(() => {
    setIsAnnotationMode(prevMode => !prevMode);
    if (controlsRef.current) {
      controlsRef.current.enabled = isAnnotationMode; // Note: This is reversed because the state hasn't updated yet
    }
  }, []);

  const onPointerDown = (event) => {
    if (!isAnnotationMode) return;
    isDrawingRef.current = true;
    const rect = canvasRef.current.getBoundingClientRect();
    mouseRef.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouseRef.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    startAnnotation();
  };

  const onPointerMove = (event) => {
    if (!isAnnotationMode || !isDrawingRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    mouseRef.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouseRef.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    updateAnnotation();
  };

  const onPointerUp = () => {
    if (!isAnnotationMode) return;
    isDrawingRef.current = false;
    finishAnnotation();
  };

  const startAnnotation = () => {
    raycasterRef.current.setFromCamera(mouseRef.current, cameraRef.current);
    const intersects = raycasterRef.current.intersectObject(pointCloudRef.current);
    if (intersects.length > 0) {
      const point = intersects[0].point;
      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array([point.x, point.y, point.z]);
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      const line = new THREE.Line(geometry, annotationMaterials[incisionType]);
      sceneRef.current.add(line);
      currentAnnotationRef.current = line;
      updateAnnotationOn2D(point);
      logAnnotation(point);
    }
  };

  const updateAnnotation = () => {
    raycasterRef.current.setFromCamera(mouseRef.current, cameraRef.current);
    const intersects = raycasterRef.current.intersectObject(pointCloudRef.current);
    if (intersects.length > 0 && currentAnnotationRef.current) {
      const newPoint = intersects[0].point;
      const positions = currentAnnotationRef.current.geometry.attributes.position;
      const newPositions = new Float32Array(positions.count * 3 + 3);
      newPositions.set(positions.array);
      newPositions[positions.count * 3] = newPoint.x;
      newPositions[positions.count * 3 + 1] = newPoint.y;
      newPositions[positions.count * 3 + 2] = newPoint.z;
      currentAnnotationRef.current.geometry.setAttribute('position', new THREE.BufferAttribute(newPositions, 3));
      currentAnnotationRef.current.geometry.attributes.position.needsUpdate = true;
      updateAnnotationOn2D(newPoint);
      logAnnotation(newPoint);
    }
  };

  const finishAnnotation = () => {
    if (currentAnnotationRef.current) {
      annotationsRef.current.push(currentAnnotationRef.current);
      currentAnnotationRef.current = null;
    }
  };

  const updateAnnotationOn2D = (point) => {
    const ctx = imageCanvasRef.current.getContext('2d');
    const imagePoint = getImagePointFromWorldPoint(point);
    if (imagePoint) {
      if (!currentAnnotationRef.current || currentAnnotationRef.current.geometry.attributes.position.count === 1) {
        ctx.beginPath();
        ctx.moveTo(imagePoint.x, imagePoint.y);
      } else {
        ctx.lineTo(imagePoint.x, imagePoint.y);
      }
      ctx.strokeStyle = annotationMaterials[incisionType].color.getStyle();
      ctx.lineWidth = incisionWidth;
      ctx.stroke();
    }
  };

  const getImagePointFromWorldPoint = (worldPoint) => {
    const geometry = pointCloudRef.current.geometry;
    const positions = geometry.attributes.position.array;
    let closestPoint = null;
    let minDistance = Infinity;

    for (let i = 0; i < positions.length; i += 3) {
      const distance = worldPoint.distanceTo(new THREE.Vector3(positions[i], positions[i+1], positions[i+2]));
      if (distance < minDistance) {
        minDistance = distance;
        closestPoint = {
          x: (positions[i] + geometry.boundingSphere.radius) * (imageCanvasRef.current.width / geometry.boundingSphere.radius / 2),
          y: (-positions[i+1] + geometry.boundingSphere.radius) * (imageCanvasRef.current.height / geometry.boundingSphere.radius / 2)
        };
      }
    }

    return closestPoint;
  };

  const logAnnotation = (point) => {
    setAnnotationLog(prevLog => [...prevLog, `${incisionType}: (${point.x.toFixed(2)}, ${point.y.toFixed(2)}, ${point.z.toFixed(2)})`]);
  };

  const drawCapturedImageOnCanvas = useCallback(() => {
    const ctx = imageCanvasRef.current.getContext('2d');
    const img = new Image();
    img.onload = () => {
      imageCanvasRef.current.width = img.width;
      imageCanvasRef.current.height = img.height;
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
      ctx.drawImage(img, 0, 0, ctx.canvas.width, ctx.canvas.height);
      redrawAnnotations();
    };
    img.src = scannedImages[currentImageIndex];
  }, [currentImageIndex, scannedImages]);

  const redrawAnnotations = () => {
    const ctx = imageCanvasRef.current.getContext('2d');
    annotationsRef.current.forEach(annotation => {
      const positions = annotation.geometry.attributes.position.array;
      ctx.beginPath();
      for (let i = 0; i < positions.length; i += 3) {
        const point = new THREE.Vector3(positions[i], positions[i+1], positions[i+2]);
        const imagePoint = getImagePointFromWorldPoint(point);
        if (imagePoint) {
          if (i === 0) {
            ctx.moveTo(imagePoint.x, imagePoint.y);
          } else {
            ctx.lineTo(imagePoint.x, imagePoint.y);
          }
        }
      }
      ctx.strokeStyle = annotation.material.color.getStyle();
      ctx.lineWidth = incisionWidth;
      ctx.stroke();
    });
  };

  useEffect(() => {
    if (scanningStage === 'processing') {
      drawCapturedImageOnCanvas();
    }
  }, [scanningStage, currentImageIndex, drawCapturedImageOnCanvas]);

  const buttonStyle = {
    padding: '15px 30px',
    fontSize: '20px',
    margin: '10px',
    cursor: 'pointer',
  };

  const textStyle = {
    fontSize: '18px',
  };


  return (
    <div style={{ display: 'flex', height: '100vh', fontSize: '18px' }}>
      <div style={{ width: '50%', padding: '20px' }}>
        <h1>Captured Images</h1>
        {scanningStage === 'idle' && (
          <button style={buttonStyle} onClick={() => setScanningStage('scanning')}>Start Scanning</button>
        )}
        {scanningStage === 'scanning' && (
          <div>
            <video ref={videoRef} autoPlay style={{ width: '100%' }} />
            <button style={buttonStyle} onClick={captureImage}>Capture Image</button>
            <button 
              style={buttonStyle} 
              onClick={() => setScanningStage('processing')} 
              disabled={scannedImages.length < 3}
            >
              Finish Scanning
            </button>
            <p style={textStyle}>Captured Images: {scannedImages.length}</p>
          </div>
        )}
        {scanningStage === 'processing' && (
          <div>
            <canvas ref={imageCanvasRef} style={{ width: '100%', height: 'auto' }} />
            <div>
              {scannedImages.map((_, index) => (
                <button 
                  key={index} 
                  style={buttonStyle}
                  onClick={() => {
                    setCurrentImageIndex(index);
                    drawCapturedImageOnCanvas();
                  }}
                >
                  Image {index + 1}
                </button>
              ))}
            </div>
          </div>
        )}
        <div style={{ marginTop: '20px' }}>
          <h2>Annotation Log</h2>
          <ul style={textStyle}>
            {annotationLog.map((log, index) => (
              <li key={index}>{log}</li>
            ))}
          </ul>
        </div>
      </div>
      <div style={{ width: '50%', padding: '20px' }}>
        <h1>3D Reconstruction</h1>
        <div ref={canvasRef} style={{ width: '100%', height: 'calc(100% - 200px)' }} />
        <div style={{ marginTop: '20px' }}>
          <h2>Incision Control</h2>
          <div style={textStyle}>
            <label>
              Incision Type:
              <select value={incisionType} onChange={(e) => setIncisionType(e.target.value)} style={buttonStyle}>
                <option value="scalpel">Scalpel</option>
                <option value="cautery">Cautery</option>
                <option value="laser">Laser</option>
              </select>
            </label>
          </div>
          <div style={textStyle}>
            <label>
              Incision Width:
              <input 
                type="range" 
                min="              1" 
                max="10" 
                value={incisionWidth} 
                onChange={(e) => setIncisionWidth(parseInt(e.target.value))} 
                style={buttonStyle} 
                />
              </label>
            </div>
          </div>
          <p>Current Mode: {isAnnotationMode ? 'Annotation' : 'Rotation'}</p>
          <p>Double-click to switch modes</p>
        </div>
      </div>
    );
  };
  
  export default App;
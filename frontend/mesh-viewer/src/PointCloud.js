import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useThree } from '@react-three/fiber';
import * as THREE from 'three';

const PointCloud = React.memo(({ points, onIncision }) => {
  const meshRef = useRef();
  const [isDrawing, setIsDrawing] = useState(false);
  const [currentPath, setCurrentPath] = useState([]);
  const { raycaster, camera } = useThree();

  useEffect(() => {
    if (meshRef.current && points.length > 0) {
      const positions = new Float32Array(points.length * 3);
      const colors = new Float32Array(points.length * 3);

      points.forEach((point, i) => {
        positions.set(point.position, i * 3);
        colors.set(point.color, i * 3);
      });

      meshRef.current.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      meshRef.current.geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    }
  }, [points]);

  const getIntersection = useCallback(
    (event) => {
      const mouse = new THREE.Vector2(
        (event.clientX / window.innerWidth) * 2 - 1,
        -(event.clientY / window.innerHeight) * 2 + 1
      );

      raycaster.setFromCamera(mouse, camera);
      const hits = raycaster.intersectObject(meshRef.current);
      return hits.length > 0 ? hits[0].point : null;
    },
    [raycaster, camera]
  );

  const handlePointerDown = (event) => {
    setIsDrawing(true);
    const point = getIntersection(event);
    if (point) {
      setCurrentPath([point]);
    }
  };

  const handlePointerMove = useCallback(
    (event) => {
      if (isDrawing) {
        const point = getIntersection(event);
        if (point) {
          setCurrentPath((prev) => [...prev, point]);
        }
      }
    },
    [isDrawing, getIntersection]
  );

  const handlePointerUp = () => {
    setIsDrawing(false);
    if (currentPath.length > 1) {
      onIncision(currentPath);
    }
    setCurrentPath([]);
  };

  return (
    <>
      <points
        ref={meshRef}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
      >
        <bufferGeometry />
        <pointsMaterial vertexColors size={0.02} sizeAttenuation transparent opacity={0.8} />
      </points>
      {currentPath.length > 1 && (
        <line>
          <bufferGeometry attach="geometry" setFromPoints={currentPath} />
          <lineBasicMaterial attach="material" color="red" linewidth={2} />
        </line>
      )}
    </>
  );
});

export default PointCloud;

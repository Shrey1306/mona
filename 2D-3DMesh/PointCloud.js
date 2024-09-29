import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useThree } from '@react-three/fiber';
import * as THREE from 'three';

const PointCloud = React.memo(({ points, onIncision }) => {
  const meshRef = useRef();
  const [isDrawing, setIsDrawing] = useState(false);
  const [currentIncision, setCurrentIncision] = useState([]);
  const { raycaster, camera } = useThree();

  useEffect(() => {
    if (meshRef.current) {
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

  const handlePointerDown = (event) => {
    setIsDrawing(true);
    const intersection = getIntersection(event);
    if (intersection) {
      setCurrentIncision([intersection]);
    }
  };

  const handlePointerMove = useCallback(
    (event) => {
      if (isDrawing) {
        const intersection = getIntersection(event);
        if (intersection) {
          setCurrentIncision((prev) => [...prev, intersection]);
        }
      }
    },
    [isDrawing]
  );

  const handlePointerUp = () => {
    setIsDrawing(false);
    if (currentIncision.length > 1) {
      onIncision(currentIncision);
    }
    setCurrentIncision([]);
  };

  const getIntersection = (event) => {
    const mouse = new THREE.Vector2(
      (event.clientX / window.innerWidth) * 2 - 1,
      -(event.clientY / window.innerHeight) * 2 + 1
    );

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObject(meshRef.current);

    if (intersects.length > 0) {
      return intersects[0].point;
    }

    return null;
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
      {currentIncision.length > 1 && (
        <line>
          <bufferGeometry attach="geometry" setFromPoints={currentIncision} />
          <lineBasicMaterial attach="material" color="red" linewidth={2} />
        </line>
      )}
    </>
  );
});

export default PointCloud;

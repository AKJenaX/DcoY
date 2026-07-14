import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";

export const Login3DBackground: React.FC = () => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [useFallback, setUseFallback] = useState(false);

  useEffect(() => {
    // 1. Accessibility check for reduced motion
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
      setUseFallback(true);
      return;
    }

    const deviceMemory = (navigator as any).deviceMemory || 8;
    if (navigator.hardwareConcurrency <= 2 && deviceMemory <= 2) {
      setUseFallback(true);
      return;
    }

    if (!containerRef.current) return;

    let scene: THREE.Scene;
    let camera: THREE.PerspectiveCamera;
    let renderer: THREE.WebGLRenderer | null = null;
    let animationFrameId = 0;
    let group: THREE.Group;
    let disposed = false;

    // Mouse positions for parallax
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const handleMouseMove = (event: MouseEvent) => {
      mouseX = (event.clientX - window.innerWidth / 2) / 100;
      mouseY = (event.clientY - window.innerHeight / 2) / 100;
    };

    window.addEventListener("mousemove", handleMouseMove);

    // Visibility observer to pause animation loop when tab is unfocused
    let isTabVisible = true;
    const handleVisibilityChange = () => {
      isTabVisible = !document.hidden;
      if (isTabVisible) {
        lastTime = performance.now();
      }
    };
    document.addEventListener("visibilitychange", handleVisibilityChange);

    const handleResize = () => {
      if (!containerRef.current || !renderer || !camera) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    const disposeWebGL = () => {
      if (disposed) return;
      disposed = true;
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("resize", handleResize);
      document.removeEventListener("visibilitychange", handleVisibilityChange);

      if (renderer?.domElement?.parentElement) {
        renderer.domElement.parentElement.removeChild(renderer.domElement);
      }
      renderer?.dispose();
    };

    // Initialization
    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;

    try {
      scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x0a0b0d, 0.012);

      camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 100);
    camera.position.z = 32;

      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setClearColor(0x0a0b0d, 1);
      containerRef.current.appendChild(renderer.domElement);
    } catch (e) {
      // Catch WebGL context initialization errors gracefully
      console.warn("WebGL initialization failed. Loading static fallback background.", e);
      disposeWebGL();
      setUseFallback(true);
      return;
    }

    // Hexagonal geometry outline vertices helper
    const size = 1.45;
    const points: THREE.Vector3[] = [];
    for (let i = 0; i <= 6; i++) {
      const angle = (i * Math.PI) / 3;
      points.push(new THREE.Vector3(Math.cos(angle) * size, Math.sin(angle) * size, 0));
    }
    const outlineGeometry = new THREE.BufferGeometry().setFromPoints(points);

    // Solid inner hexagon geometry for lit cells
    const fillGeometry = new THREE.CircleGeometry(size * 0.95, 6);

    // Group to hold all lattice cells
    group = new THREE.Group();
    scene.add(group);

    // Lattice arrangements
    const hexCountX = Math.min(28, Math.ceil(width / 64));
    const hexCountY = Math.min(20, Math.ceil(height / 58));
    const spacingX = size * 1.5;
    const spacingY = size * Math.sqrt(3);

    const lineMaterial = new THREE.LineBasicMaterial({
      color: 0x1e293b,
      transparent: true,
      opacity: 0.42,
    });

    const activeAmberMaterial = new THREE.MeshBasicMaterial({
      color: 0xf5a623,
      transparent: true,
      opacity: 0.14,
      side: THREE.DoubleSide,
    });

    const activeCyanMaterial = new THREE.MeshBasicMaterial({
      color: 0x00e5ff,
      transparent: true,
      opacity: 0.11,
      side: THREE.DoubleSide,
    });

    // Populate lattice
    const litCells: { mesh: THREE.Mesh; baseOpacity: number; speed: number; phase: number }[] = [];

    for (let x = -hexCountX / 2; x <= hexCountX / 2; x++) {
      for (let y = -hexCountY / 2; y <= hexCountY / 2; y++) {
        const posX = x * spacingX;
        const posY = y * spacingY + (Math.abs(x) % 2 === 1 ? spacingY / 2 : 0);
        const posZ = (Math.random() - 0.5) * 1.5; // slight organic depth variance

        // Wireframe Hexagon border
        const line = new THREE.LineLoop(outlineGeometry, lineMaterial);
        line.position.set(posX, posY, posZ);
        group.add(line);

        // Scattered glows inside grid cells
        const rand = Math.random();
        if (rand < 0.32) {
          const isAmber = rand < 0.16;
          const fillMesh = new THREE.Mesh(fillGeometry, isAmber ? activeAmberMaterial : activeCyanMaterial);
          fillMesh.position.set(posX, posY, posZ - 0.1);
          group.add(fillMesh);

          litCells.push({
            mesh: fillMesh,
            baseOpacity: isAmber ? 0.16 : 0.12,
            speed: 1 + Math.random() * 2,
            phase: Math.random() * Math.PI * 2,
          });
        }
      }
    }

    // Add subtle ambient and point lights to tint fog and meshes
    const ambientLight = new THREE.AmbientLight(0x0a0b0d);
    scene.add(ambientLight);

    const amberLight = new THREE.PointLight(0xf5a623, 2, 40);
    amberLight.position.set(-15, 10, 10);
    scene.add(amberLight);

    const cyanLight = new THREE.PointLight(0x00e5ff, 2, 40);
    cyanLight.position.set(15, -10, 10);
    scene.add(cyanLight);

    // Performance/FPS observer parameters
    let lastTime = performance.now();
    let frameCount = 0;
    let consecutiveLowFps = 0;

    // Animation Render Loop
    const animate = (timeNow: number) => {
      if (!isTabVisible) {
        animationFrameId = requestAnimationFrame(animate);
        return;
      }

      // Check frame budget to detect low performance
      const delta = timeNow - lastTime;
      lastTime = timeNow;
      frameCount++;

      if (frameCount > 90) {
        const fps = 1000 / delta;
        if (fps < 30) {
          consecutiveLowFps++;
          if (consecutiveLowFps > 12) {
            console.warn("Sub-30 FPS detected. Downgrading WebGL render to static fallback.");
            disposeWebGL();
            setUseFallback(true);
            return;
          }
        } else {
          consecutiveLowFps = 0;
        }
      }

      // Slow organic atmospheric group drift rotation
      group.rotation.z = Math.sin(timeNow * 0.00005) * 0.05;
      group.rotation.x = Math.sin(timeNow * 0.00003) * 0.03;

      // Pulse lit cells opacity smoothly
      litCells.forEach((cell) => {
        const pulse = Math.sin(timeNow * 0.001 * cell.speed + cell.phase);
        const mat = cell.mesh.material as THREE.MeshBasicMaterial;
        mat.opacity = cell.baseOpacity + pulse * 0.04;
      });

      // Smooth mouse-parallax interpolation
      targetX += (mouseX - targetX) * 0.05;
      targetY += (mouseY - targetY) * 0.05;
      camera.position.x = targetX * 3;
      camera.position.y = -targetY * 3;
      camera.lookAt(scene.position);

      renderer?.render(scene, camera);
      animationFrameId = requestAnimationFrame(animate);
    };

    animationFrameId = requestAnimationFrame(animate);

    window.addEventListener("resize", handleResize);

    // Cleanup Loop
    return () => {
      disposeWebGL();
    };
  }, []);

  if (useFallback) {
    return (
      <div className="w-full h-full bg-[#0a0b0d] login-honeycomb-fallback" />
    );
  }

  return (
    <div ref={containerRef} className="w-full h-full overflow-hidden absolute inset-0 bg-[#0a0b0d]" />
  );
};

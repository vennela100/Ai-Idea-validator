// Three.js animations and 3D effects for AI Business Idea Validator
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.150.0/build/three.module.js';

class ThreeAnimations {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.brain = null;
        this.particles = null;
        this.featureCards = [];
        this.charts = [];
        this.mouse = { x: 0, y: 0 };
        this.scrollY = 0;
        this.isInitialized = false;
    }

    // Initialize Three.js scene
    init(container) {
        if (this.isInitialized) return;
        
        this.container = container;
        this.width = container.clientWidth;
        this.height = container.clientHeight;
        
        // Scene setup
        this.scene = new THREE.Scene();
        this.scene.fog = new THREE.Fog(0x020617, 1, 15);
        
        // Camera setup
        this.camera = new THREE.PerspectiveCamera(75, this.width / this.height, 0.1, 1000);
        this.camera.position.z = 5;
        
        // Renderer setup
        this.renderer = new THREE.WebGLRenderer({ 
            alpha: true, 
            antialias: true,
            powerPreference: "high-performance"
        });
        this.renderer.setSize(this.width, this.height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(this.renderer.domElement);
        
        // Lighting
        this.setupLighting();
        
        // Create 3D elements
        this.createAIBrain();
        this.createParticles();
        this.createFeatureCards();
        
        // Event listeners
        this.setupEventListeners();
        
        // Start animation loop
        this.animate();
        
        this.isInitialized = true;
    }

    // Setup dynamic lighting
    setupLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
        this.scene.add(ambientLight);
        
        // Main directional light
        const directionalLight = new THREE.DirectionalLight(0x7C3AED, 1);
        directionalLight.position.set(5, 5, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.camera.near = 0.1;
        directionalLight.shadow.camera.far = 50;
        directionalLight.shadow.camera.left = -10;
        directionalLight.shadow.camera.right = 10;
        directionalLight.shadow.camera.top = 10;
        directionalLight.shadow.camera.bottom = -10;
        this.scene.add(directionalLight);
        
        // Accent light
        const accentLight = new THREE.PointLight(0x06B6D4, 1, 10);
        accentLight.position.set(-3, 2, 2);
        this.scene.add(accentLight);
        
        // Dynamic lights
        this.dynamicLights = [
            new THREE.PointLight(0x7C3AED, 0.5, 5),
            new THREE.PointLight(0x06B6D4, 0.5, 5)
        ];
        
        this.dynamicLights[0].position.set(2, -1, 3);
        this.dynamicLights[1].position.set(-2, 1, -3);
        
        this.scene.add(...this.dynamicLights);
    }

    // Create 3D rotating AI brain
    createAIBrain() {
        const brainGroup = new THREE.Group();
        
        // Brain core
        const coreGeometry = new THREE.IcosahedronGeometry(1, 2);
        const coreMaterial = new THREE.MeshPhongMaterial({
            color: 0x7C3AED,
            emissive: 0x7C3AED,
            emissiveIntensity: 0.2,
            shininess: 100,
            specular: 0x06B6D4
        });
        
        const brainCore = new THREE.Mesh(coreGeometry, coreMaterial);
        brainCore.castShadow = true;
        brainCore.receiveShadow = true;
        brainGroup.add(brainCore);
        
        // Neural network connections
        const connectionGeometry = new THREE.BufferGeometry();
        const connectionMaterial = new THREE.LineBasicMaterial({
            color: 0x06B6D4,
            transparent: true,
            opacity: 0.6
        });
        
        const positions = [];
        const nodeCount = 20;
        const nodes = [];
        
        // Create nodes
        for (let i = 0; i < nodeCount; i++) {
            const phi = Math.acos(-1 + (2 * i) / nodeCount);
            const theta = Math.sqrt(nodeCount * Math.PI) * phi;
            
            const x = 1.5 * Math.cos(theta) * Math.sin(phi);
            const y = 1.5 * Math.sin(theta) * Math.sin(phi);
            const z = 1.5 * Math.cos(phi);
            
            nodes.push(new THREE.Vector3(x, y, z));
            
            // Add node spheres
            const nodeGeometry = new THREE.SphereGeometry(0.05, 8, 8);
            const nodeMaterial = new THREE.MeshPhongMaterial({
                color: 0x06B6D4,
                emissive: 0x06B6D4,
                emissiveIntensity: 0.3
            });
            
            const nodeMesh = new THREE.Mesh(nodeGeometry, nodeMaterial);
            nodeMesh.position.set(x, y, z);
            brainGroup.add(nodeMesh);
        }
        
        // Create connections
        for (let i = 0; i < nodeCount; i++) {
            for (let j = i + 1; j < nodeCount; j++) {
                if (Math.random() > 0.7) {
                    positions.push(nodes[i].x, nodes[i].y, nodes[i].z);
                    positions.push(nodes[j].x, nodes[j].y, nodes[j].z);
                }
            }
        }
        
        connectionGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        const connections = new THREE.LineSegments(connectionGeometry, connectionMaterial);
        brainGroup.add(connections);
        
        // Add pulsing core
        const pulseGeometry = new THREE.SphereGeometry(0.3, 16, 16);
        const pulseMaterial = new THREE.MeshBasicMaterial({
            color: 0x06B6D4,
            transparent: true,
            opacity: 0
        });
        
        const pulse = new THREE.Mesh(pulseGeometry, pulseMaterial);
        brainGroup.add(pulse);
        
        this.brain = {
            group: brainGroup,
            core: brainCore,
            pulse: pulse,
            connections: connections,
            rotationSpeed: 0.005
        };
        
        this.scene.add(brainGroup);
    }

    // Create interactive particle background
    createParticles() {
        const particleCount = 200;
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        const sizes = new Float32Array(particleCount);
        
        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 20;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 20;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 20;
            
            const color = new THREE.Color();
            color.setHSL(Math.random() * 0.2 + 0.5, 0.8, 0.6);
            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;
            
            sizes[i] = Math.random() * 0.1 + 0.05;
        }
        
        const particleGeometry = new THREE.BufferGeometry();
        particleGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        particleGeometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        particleGeometry.setAttribute('size', new THREE.Float32BufferAttribute(sizes, 1));
        
        const particleMaterial = new THREE.PointsMaterial({
            size: 0.1,
            vertexColors: true,
            transparent: true,
            opacity: 0.8,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });
        
        this.particles = new THREE.Points(particleGeometry, particleMaterial);
        this.scene.add(this.particles);
    }

    // Create floating feature cards
    createFeatureCards() {
        const features = [
            { icon: '🧠', title: 'AI Analysis', color: 0x7C3AED, position: [-3, 1, 0] },
            { icon: '📊', title: 'Market Research', color: 0x06B6D4, position: [3, 1, 0] },
            { icon: '🎯', title: 'Target Analysis', color: 0x2563EB, position: [-3, -1, 0] },
            { icon: '🚀', title: 'Growth Strategy', color: 0x10B981, position: [3, -1, 0] }
        ];
        
        features.forEach((feature, index) => {
            const cardGroup = new THREE.Group();
            
            // Card background
            const cardGeometry = new THREE.BoxGeometry(1.5, 0.8, 0.1);
            const cardMaterial = new THREE.MeshPhongMaterial({
                color: feature.color,
                emissive: feature.color,
                emissiveIntensity: 0.1,
                transparent: true,
                opacity: 0.8,
                side: THREE.DoubleSide
            });
            
            const card = new THREE.Mesh(cardGeometry, cardMaterial);
            card.castShadow = true;
            card.receiveShadow = true;
            cardGroup.add(card);
            
            // Icon (represented as glowing sphere)
            const iconGeometry = new THREE.SphereGeometry(0.2, 16, 16);
            const iconMaterial = new THREE.MeshBasicMaterial({
                color: 0xffffff,
                emissive: 0xffffff,
                emissiveIntensity: 0.5
            });
            
            const icon = new THREE.Mesh(iconGeometry, iconMaterial);
            icon.position.z = 0.1;
            cardGroup.add(icon);
            
            // Set initial position
            cardGroup.position.set(...feature.position);
            cardGroup.userData = { feature, index };
            
            this.featureCards.push(cardGroup);
            this.scene.add(cardGroup);
        });
    }

    // Create 3D charts for analytics
    createCharts(container) {
        // Bar chart
        this.createBarChart(container);
        
        // Pie chart
        this.createPieChart(container);
        
        // Line chart
        this.createLineChart(container);
    }

    createBarChart(container) {
        const chartGroup = new THREE.Group();
        
        const data = [65, 80, 45, 90, 75];
        const colors = [0x7C3AED, 0x06B6D4, 0x2563EB, 0x10B981, 0xF59E0B];
        
        data.forEach((value, index) => {
            const height = value / 100 * 2;
            const barGeometry = new THREE.BoxGeometry(0.3, height, 0.3);
            const barMaterial = new THREE.MeshPhongMaterial({
                color: colors[index],
                emissive: colors[index],
                emissiveIntensity: 0.1
            });
            
            const bar = new THREE.Mesh(barGeometry, barMaterial);
            bar.position.x = (index - 2) * 0.5;
            bar.position.y = height / 2;
            bar.castShadow = true;
            
            chartGroup.add(bar);
        });
        
        chartGroup.position.set(0, 0, -2);
        this.charts.push(chartGroup);
        this.scene.add(chartGroup);
    }

    createPieChart(container) {
        const chartGroup = new THREE.Group();
        const data = [30, 25, 20, 15, 10];
        const colors = [0x7C3AED, 0x06B6D4, 0x2563EB, 0x10B981, 0xF59E0B];
        
        let startAngle = 0;
        data.forEach((value, index) => {
            const angle = (value / 100) * Math.PI * 2;
            const geometry = new THREE.CylinderGeometry(0.8, 0.8, 0.1, 32, 1, false, startAngle, angle);
            const material = new THREE.MeshPhongMaterial({
                color: colors[index],
                emissive: colors[index],
                emissiveIntensity: 0.1
            });
            
            const segment = new THREE.Mesh(geometry, material);
            segment.castShadow = true;
            
            chartGroup.add(segment);
            startAngle += angle;
        });
        
        chartGroup.position.set(0, 0, 0);
        this.charts.push(chartGroup);
        this.scene.add(chartGroup);
    }

    createLineChart(container) {
        const chartGroup = new THREE.Group();
        
        const points = [];
        const data = [0.5, 0.8, 0.3, 0.9, 0.6, 1.0, 0.7];
        
        data.forEach((value, index) => {
            points.push(new THREE.Vector3((index - 3) * 0.5, value * 2, 0));
        });
        
        const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
        const lineMaterial = new THREE.LineBasicMaterial({
            color: 0x06B6D4,
            linewidth: 3
        });
        
        const line = new THREE.Line(lineGeometry, lineMaterial);
        chartGroup.add(line);
        
        // Add points
        points.forEach(point => {
            const pointGeometry = new THREE.SphereGeometry(0.05, 8, 8);
            const pointMaterial = new THREE.MeshPhongMaterial({
                color: 0x06B6D4,
                emissive: 0x06B6D4,
                emissiveIntensity: 0.3
            });
            
            const pointMesh = new THREE.Mesh(pointGeometry, pointMaterial);
            pointMesh.position.copy(point);
            chartGroup.add(pointMesh);
        });
        
        chartGroup.position.set(0, 0, 2);
        this.charts.push(chartGroup);
        this.scene.add(chartGroup);
    }

    // Setup event listeners
    setupEventListeners() {
        // Mouse movement
        window.addEventListener('mousemove', (event) => {
            this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        });
        
        // Scroll
        window.addEventListener('scroll', () => {
            this.scrollY = window.scrollY;
        });
        
        // Resize
        window.addEventListener('resize', () => this.onWindowResize());
        
        // Touch events for mobile
        window.addEventListener('touchmove', (event) => {
            if (event.touches.length > 0) {
                this.mouse.x = (event.touches[0].clientX / window.innerWidth) * 2 - 1;
                this.mouse.y = -(event.touches[0].clientY / window.innerHeight) * 2 + 1;
            }
        });
    }

    // Handle window resize
    onWindowResize() {
        if (!this.container) return;
        
        this.width = this.container.clientWidth;
        this.height = this.container.clientHeight;
        
        this.camera.aspect = this.width / this.height;
        this.camera.updateProjectionMatrix();
        
        this.renderer.setSize(this.width, this.height);
    }

    // Animation loop
    animate() {
        requestAnimationFrame(() => this.animate());
        
        if (!this.isInitialized) return;
        
        // Rotate AI brain
        if (this.brain) {
            this.brain.group.rotation.x += this.brain.rotationSpeed;
            this.brain.group.rotation.y += this.brain.rotationSpeed * 0.7;
            
            // Pulse effect
            const pulseScale = 1 + Math.sin(Date.now() * 0.002) * 0.1;
            this.brain.pulse.scale.set(pulseScale, pulseScale, pulseScale);
            this.brain.pulse.material.opacity = Math.sin(Date.now() * 0.003) * 0.3 + 0.3;
        }
        
        // Animate particles
        if (this.particles) {
            this.particles.rotation.x += 0.0005;
            this.particles.rotation.y += 0.001;
            
            // Mouse interaction
            this.particles.position.x = this.mouse.x * 0.5;
            this.particles.position.y = this.mouse.y * 0.5;
        }
        
        // Animate feature cards
        this.featureCards.forEach((card, index) => {
            const time = Date.now() * 0.001;
            
            // Floating animation
            card.position.y += Math.sin(time + index) * 0.002;
            card.rotation.y = Math.sin(time * 0.5 + index) * 0.1;
            
            // Hover effect
            const distance = Math.abs(this.mouse.x - card.position.x / 3);
            if (distance < 1) {
                card.position.z = Math.sin(time * 2) * 0.2;
                card.rotation.z = this.mouse.x * 0.1;
            }
        });
        
        // Animate charts
        this.charts.forEach((chart, index) => {
            const time = Date.now() * 0.001;
            chart.rotation.y = Math.sin(time * 0.3 + index) * 0.1;
        });
        
        // Animate dynamic lights
        this.dynamicLights.forEach((light, index) => {
            const time = Date.now() * 0.001;
            light.position.x = Math.sin(time + index) * 2;
            light.position.y = Math.cos(time * 0.7 + index) * 2;
            light.intensity = 0.3 + Math.sin(time * 2 + index) * 0.2;
        });
        
        // Parallax scrolling
        if (this.scrollY > 0) {
            this.scene.position.y = this.scrollY * 0.001;
        }
        
        // Camera movement based on mouse
        this.camera.position.x = this.mouse.x * 0.5;
        this.camera.position.y = this.mouse.y * 0.5;
        this.camera.lookAt(0, 0, 0);
        
        // Render
        this.renderer.render(this.scene, this.camera);
    }

    // Performance optimization
    dispose() {
        if (!this.isInitialized) return;
        
        // Dispose geometries
        this.scene.traverse((object) => {
            if (object.geometry) {
                object.geometry.dispose();
            }
            
            if (object.material) {
                if (Array.isArray(object.material)) {
                    object.material.forEach(material => material.dispose());
                } else {
                    object.material.dispose();
                }
            }
        });
        
        // Remove event listeners
        window.removeEventListener('mousemove', this.onMouseMove);
        window.removeEventListener('scroll', this.onScroll);
        window.removeEventListener('resize', this.onWindowResize);
        
        // Remove renderer
        if (this.renderer) {
            this.renderer.dispose();
            this.container.removeChild(this.renderer.domElement);
        }
        
        this.isInitialized = false;
    }
}

// Export for use in templates
window.ThreeAnimations = ThreeAnimations;

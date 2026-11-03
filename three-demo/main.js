import * as THREE from 'three';

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111118);
scene.fog = new THREE.Fog(0x111118, 8, 20);

const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 100);
camera.position.set(0, 2, 6);

// 조명
scene.add(new THREE.AmbientLight(0xffffff, 0.4));
const light = new THREE.DirectionalLight(0xffffff, 2);
light.position.set(4, 6, 3);
light.castShadow = true;
scene.add(light);

// 바닥
const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(30, 30),
  new THREE.MeshStandardMaterial({ color: 0x222233 })
);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -1.2;
floor.receiveShadow = true;
scene.add(floor);

// 회전하는 도형들
const cube = new THREE.Mesh(
  new THREE.BoxGeometry(1.4, 1.4, 1.4),
  new THREE.MeshStandardMaterial({ color: 0xff6b6b, roughness: 0.4 })
);
cube.position.x = -2.2;

const sphere = new THREE.Mesh(
  new THREE.SphereGeometry(0.9, 48, 32),
  new THREE.MeshStandardMaterial({ color: 0x4ecdc4, metalness: 0.5, roughness: 0.2 })
);

const torus = new THREE.Mesh(
  new THREE.TorusKnotGeometry(0.6, 0.22, 128, 16),
  new THREE.MeshStandardMaterial({ color: 0xffe66d, metalness: 0.3, roughness: 0.3 })
);
torus.position.x = 2.2;

for (const m of [cube, sphere, torus]) {
  m.castShadow = true;
  scene.add(m);
}

// 마우스에 따라 카메라 이동
const mouse = { x: 0, y: 0 };
addEventListener('pointermove', (e) => {
  mouse.x = (e.clientX / innerWidth) * 2 - 1;
  mouse.y = (e.clientY / innerHeight) * 2 - 1;
});

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

const clock = new THREE.Clock();
renderer.setAnimationLoop(() => {
  const t = clock.getElapsedTime();
  cube.rotation.set(t * 0.6, t * 0.8, 0);
  torus.rotation.set(t * 0.5, t * 0.3, 0);
  sphere.position.y = Math.sin(t * 2) * 0.4;

  camera.position.x += (mouse.x * 2 - camera.position.x) * 0.05;
  camera.position.y += (2 - mouse.y * 1.5 - camera.position.y) * 0.05;
  camera.lookAt(0, 0, 0);

  renderer.render(scene, camera);
});

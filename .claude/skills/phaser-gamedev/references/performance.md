# Performance Optimization in Phaser 3

Strategies for maintaining smooth 60fps gameplay.

## Object Pooling

The most impactful optimization. Reuse inactive instances instead of creating/destroying objects continuously—eliminates GC pauses that cause stuttering.

```javascript
// Create pool in create()
this.bulletPool = this.physics.add.group({
  defaultKey: 'bullet',
  maxSize: 100
});

// Acquire from pool
fire(x, y, vx, vy) {
  const bullet = this.bulletPool.get(x, y);
  if (!bullet) return;  // Pool exhausted
  bullet.setActive(true).setVisible(true);
  bullet.body.enable = true;
  bullet.body.setVelocity(vx, vy);
}

// Return to pool
killBullet(bullet) {
  bullet.setActive(false).setVisible(false);
  bullet.body.enable = false;
  bullet.body.stop();
}
```

## Texture Atlases

Combine sprites into a single texture to reduce draw calls and HTTP requests.

```javascript
// Load atlas (created with TexturePacker or similar)
this.load.atlas('sprites', 'assets/sprites.png', 'assets/sprites.json');

// Use frames from atlas
const player = this.add.sprite(x, y, 'sprites', 'player_idle_0');
this.anims.create({
  key: 'walk',
  frames: this.anims.generateFrameNames('sprites', {
    prefix: 'player_walk_',
    start: 0,
    end: 7
  }),
  frameRate: 10,
  repeat: -1
});
```

## Camera Culling

Phaser automatically culls off-screen sprites and images. Ensure it's working:

```javascript
// Verify culling is active (default: true)
this.cameras.main.disableCull = false;

// For large worlds, set explicit cull padding
layer.setCullPadding(2, 2);  // Extra tiles around viewport

// Check how many tiles are being rendered
console.log('Visible tiles:', groundLayer.culledTiles.length);
```

## Physics Optimization

```javascript
// Disable physics on off-screen bodies
enemies.children.iterate(enemy => {
  if (!this.cameras.main.worldView.contains(enemy.x, enemy.y)) {
    enemy.body.enable = false;
  } else {
    enemy.body.enable = true;
  }
});

// Use simpler collision shapes
// Circles are faster than rectangles
sprite.body.setCircle(16);

// Spatial hash for large numbers of bodies (>5000)
physics: {
  arcade: { useTree: false }
}

// Reduce unnecessary collision pairs
// Only add colliders you actually need
```

## Update Loop Best Practices

```javascript
// Never create objects in update()—allocates memory every frame
// Bad:
update() {
  const pos = new Phaser.Math.Vector2(this.player.x, this.player.y); // BAD
}

// Good: pre-allocate
create() {
  this._tempVec = new Phaser.Math.Vector2();
}
update() {
  this._tempVec.set(this.player.x, this.player.y); // Reuse
}

// Throttle expensive operations
update(time, delta) {
  // AI runs every 200ms, not every frame
  if (time > this._nextAiUpdate) {
    this._nextAiUpdate = time + 200;
    this.updateEnemyAI();
  }

  // Critical: player movement runs every frame
  this.updatePlayer(delta);
}
```

## Rendering Improvements

```javascript
// Batch similar sprites (automatic with texture atlases)

// Avoid expensive blend modes
sprite.blendMode = Phaser.BlendModes.NORMAL;  // Cheapest

// Limit particles
this.add.particles(x, y, 'spark', {
  maxParticles: 50,  // Cap particle count
  lifespan: 500,
  speed: { min: 50, max: 150 }
});

// Use renderTexture to cache complex static scenes
const rt = this.add.renderTexture(0, 0, 800, 600);
rt.draw(complexGroup);  // Bake to texture
complexGroup.destroy(); // Remove originals
```

## Monitoring Performance

```javascript
// Built-in FPS display
this.game.config.fps = {
  target: 60,
  forceSetTimeOut: false,
  deltaHistory: 10,
  panicMax: 120
};

// Show FPS counter
this.add.text(16, 16, '', { fontSize: '12px' })
  .setScrollFactor(0)
  .setDepth(1000);

update() {
  fpsText.setText('FPS: ' + Math.round(this.game.loop.actualFps));
}

// Chrome DevTools Performance tab
// Look for: long GC pauses, excessive draw calls, memory growth
```

## Summary Checklist

- [ ] Object pooling for bullets, particles, enemies
- [ ] Texture atlas instead of individual images
- [ ] No `new` allocations inside `update()`
- [ ] Throttle AI/pathfinding to intervals
- [ ] Limit particle `maxParticles`
- [ ] Disable physics bodies for off-screen objects
- [ ] `roundPixels: true` for pixel-art games (prevents sub-pixel blurring)
- [ ] Monitor actual FPS during development

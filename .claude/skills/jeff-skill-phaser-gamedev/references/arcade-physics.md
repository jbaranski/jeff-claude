# Arcade Physics Deep Dive

Comprehensive reference for Phaser 3 Arcade Physics system.

## World Configuration

```javascript
// In game config
physics: {
  default: 'arcade',
  arcade: {
    gravity: { x: 0, y: 300 },
    debug: true,                    // Show collision bodies
    debugShowBody: true,
    debugShowStaticBody: true,
    debugShowVelocity: true,
    debugBodyColor: 0xff00ff,
    debugStaticBodyColor: 0x0000ff,
    debugVelocityColor: 0x00ff00,
    fps: 60,                        // Physics update rate
    timeScale: 1,                   // 0.5 = half speed, 2 = double
    checkCollision: {
      up: true,
      down: true,
      left: true,
      right: true
    },
    overlapBias: 4,                 // Overlap tolerance
    tileBias: 16,                   // Tile collision bias
    forceX: false,                  // Prioritize X-axis separation
    maxEntries: 16,                 // RTree max entries per node
    useTree: true                   // RTree for broad-phase; set false with >5000 dynamic bodies
  }
}
```

## Body Types

### Dynamic Bodies

Move, respond to velocity, gravity, and collisions.

```javascript
// Create with physics enabled
const player = this.physics.add.sprite(100, 100, 'player');

// Or add to existing sprite
const sprite = this.add.sprite(100, 100, 'player');
this.physics.add.existing(sprite);

// Body properties
player.body.setVelocity(100, -200);
player.body.setVelocityX(100);
player.body.setVelocityY(-200);
player.body.setBounce(0.5, 0.5);
player.body.setDrag(100, 100);
player.body.setFriction(0.5, 0.5);
player.body.setMaxVelocity(300, 400);
player.body.setGravityY(500); // Additional gravity
player.body.setAcceleration(100, 0);
player.body.setCollideWorldBounds(true);
player.body.onWorldBounds = true; // Enable worldbounds event
```

### Static Bodies

Immovable, no velocity or gravity response. Efficient for platforms.

```javascript
// Create static group
const platforms = this.physics.add.staticGroup();
platforms.create(400, 568, 'ground');

// Or give an existing game object a static body
this.physics.add.existing(sprite, true); // true = static

// After scaling/moving static bodies
sprite.refreshBody();

// A dynamic body that other bodies can't push (still moves under its own velocity)
mover.body.setImmovable(true);
```

## Body Sizing and Shape

```javascript
// Custom body size
sprite.body.setSize(width, height, center);
sprite.body.setSize(32, 48, true); // Centered

// Offset body from sprite
sprite.body.setOffset(x, y);

// Circular body (for rolling objects)
sprite.body.setCircle(radius, offsetX, offsetY);
sprite.body.setCircle(16, 0, 0);
```

## Collision Detection

### Collider vs Overlap

```javascript
// Collider: Physical collision, objects separate
this.physics.add.collider(player, platforms);
this.physics.add.collider(player, enemies, hitEnemy, null, this);

// Overlap: Detect overlap without physical response
this.physics.add.overlap(player, coins, collectCoin, null, this);

function collectCoin(player, coin) {
  coin.disableBody(true, true); // (disableGameObject, hideGameObject)
}
```

### Collision Callbacks

```javascript
// Process callback (return false to skip collision)
function shouldCollide(player, enemy) {
  return !player.isInvincible;
}

this.physics.add.collider(player, enemies, hitEnemy, shouldCollide, this);
```

### Collision Events

```javascript
// World bounds event
this.physics.world.on('worldbounds', (body, up, down, left, right) => {
  if (down) {
    // Hit bottom of world
  }
});

// Enable on body first
player.body.onWorldBounds = true;
player.body.setCollideWorldBounds(true);
```

## Groups

### Static Groups

```javascript
const platforms = this.physics.add.staticGroup();

// Add children
platforms.create(400, 568, 'ground');
platforms.createMultiple({
  key: 'brick',
  repeat: 10,
  setXY: { x: 50, y: 300, stepX: 70 }
});

// After modifying
platforms.refresh();
```

### Dynamic Groups

```javascript
const enemies = this.physics.add.group({
  key: 'enemy',
  repeat: 5,
  setXY: { x: 100, y: 0, stepX: 100 }
});

// Group defaults
const bullets = this.physics.add.group({
  defaultKey: 'bullet',
  maxSize: 50,
  runChildUpdate: true, // Call update() on children
  collideWorldBounds: true,
  velocityY: -300
});

// Iterate children
enemies.children.iterate((enemy) => {
  enemy.setBounce(0.5);
});

// Get first inactive (for pooling)
const bullet = bullets.get(x, y);
if (bullet) {
  bullet.setActive(true).setVisible(true);
  bullet.body.enable = true;
}
```

## Object Pooling

Reuse objects instead of create/destroy for performance.

```javascript
// In create()
this.bulletPool = this.physics.add.group({
  defaultKey: 'bullet',
  maxSize: 100,
  createCallback: (bullet) => {
    bullet.setName('bullet' + this.bulletPool.getLength());
  }
});

// Fire bullet
fire(x, y, velocityX, velocityY) {
  const bullet = this.bulletPool.get(x, y);
  if (bullet) {
    bullet.setActive(true);
    bullet.setVisible(true);
    bullet.body.enable = true;
    bullet.body.setVelocity(velocityX, velocityY);
  }
}

// Return to pool
killBullet(bullet) {
  bullet.setActive(false);
  bullet.setVisible(false);
  bullet.body.enable = false;
  bullet.body.stop();
}
```

## Movement Patterns

### Basic Movement

```javascript
update(time, delta) {
  const speed = 160;

  player.setVelocity(0);

  if (cursors.left.isDown) {
    player.setVelocityX(-speed);
  } else if (cursors.right.isDown) {
    player.setVelocityX(speed);
  }

  if (cursors.up.isDown) {
    player.setVelocityY(-speed);
  } else if (cursors.down.isDown) {
    player.setVelocityY(speed);
  }
}
```

### Platformer Movement

```javascript
update(time, delta) {
  // Horizontal movement
  if (cursors.left.isDown) {
    player.setVelocityX(-160);
    player.anims.play('walk', true);
    player.flipX = true;
  } else if (cursors.right.isDown) {
    player.setVelocityX(160);
    player.anims.play('walk', true);
    player.flipX = false;
  } else {
    player.setVelocityX(0);
    player.anims.play('idle', true);
  }

  // Jump (only when grounded)
  if (cursors.up.isDown && player.body.blocked.down) {
    player.setVelocityY(-330);
  }
}
```

### Acceleration-Based Movement

```javascript
const accel = 600;
const maxSpeed = 200;
const drag = 400;

player.body.setMaxVelocity(maxSpeed);
player.body.setDrag(drag, 0);

update() {
  if (cursors.left.isDown) {
    player.body.setAccelerationX(-accel);
  } else if (cursors.right.isDown) {
    player.body.setAccelerationX(accel);
  } else {
    player.body.setAccelerationX(0);
  }
}
```

## Velocity Helpers

```javascript
// Move to point
this.physics.moveTo(sprite, targetX, targetY, speed);

// Move to object
this.physics.moveToObject(sprite, target, speed);

// Accelerate to point
this.physics.accelerateTo(sprite, targetX, targetY, accel, maxSpeedX, maxSpeedY);

// Velocity from angle
this.physics.velocityFromAngle(angle, speed, outVelocity);
this.physics.velocityFromRotation(rotation, speed, outVelocity);
```

## Checking Collisions

```javascript
// Touch flags (in update)
if (player.body.blocked.down) {
  // On ground
}

if (player.body.blocked.left || player.body.blocked.right) {
  // Hitting wall
}

// Touching another body
if (player.body.touching.down) {
  // Standing on something
}

// Was touching last frame
if (player.body.wasTouching.down && !player.body.touching.down) {
  // Just left ground
}

// Overlapping check
const overlapping = this.physics.overlap(player, enemy);

// Distance check
const distance = Phaser.Math.Distance.Between(player.x, player.y, enemy.x, enemy.y);
```

## World Bounds

```javascript
// Set world bounds
this.physics.world.setBounds(0, 0, 3000, 600);

// Different bounds per side
this.physics.world.setBoundsCollision(true, true, true, false); // No bottom

// Camera follows player in larger world
this.cameras.main.setBounds(0, 0, 3000, 600);
this.cameras.main.startFollow(player);
```

## Debug Visualization

```javascript
// Toggle debug at runtime (debugGraphic only exists if debug was on at startup)
if (!this.physics.world.debugGraphic) this.physics.world.createDebugGraphic();
this.physics.world.drawDebug = !this.physics.world.drawDebug;
this.physics.world.debugGraphic.clear();

// Custom debug rendering
const graphics = this.add.graphics();

this.physics.world.on('worldstep', () => {
  graphics.clear();

  enemies.children.iterate((enemy) => {
    graphics.strokeCircle(enemy.body.center.x, enemy.body.center.y, enemy.body.halfWidth);
  });
});
```

## Common Patterns

### One-Way Platforms

```javascript
// In process callback
function oneWayPlatform(player, platform) {
  // Only collide if player is falling and above platform
  if (player.body.velocity.y > 0 && player.body.bottom <= platform.body.top + 10) {
    return true;
  }
  return false;
}

this.physics.add.collider(player, platforms, null, oneWayPlatform, this);
```

### Knockback

```javascript
function hitEnemy(player, enemy) {
  const knockbackForce = 200;
  const direction = player.x < enemy.x ? -1 : 1;

  player.setVelocity(direction * knockbackForce, -knockbackForce);
  player.isInvincible = true;

  this.time.delayedCall(1000, () => {
    player.isInvincible = false;
  });
}
```

### Moving Platforms

Drive the platform with velocity, not a tween: a tween sets `x` directly, so the body has no
velocity and riders slide off. With velocity plus friction, Arcade carries whatever stands on it.

```javascript
// In create()
this.movingPlatform = this.physics.add.image(400, 400, 'platform');
this.movingPlatform.body.setImmovable(true).setAllowGravity(false).setFriction(1, 0);
this.movingPlatform.body.setVelocityX(100);
this.physics.add.collider(player, this.movingPlatform);

// In update(): reverse at the ends of its track
if (this.movingPlatform.x >= 600) this.movingPlatform.body.setVelocityX(-100);
else if (this.movingPlatform.x <= 400) this.movingPlatform.body.setVelocityX(100);
```

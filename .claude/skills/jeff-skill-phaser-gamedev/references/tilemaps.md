# Tilemaps Reference

Comprehensive guide for Phaser 3 tilemap integration with Tiled Map Editor.

---

## Tiled Map Editor Fundamentals

### Tileset Types

| Type                 | Description                                        | Use Case                                 |
| -------------------- | -------------------------------------------------- | ---------------------------------------- |
| **Image-based**      | Single image with fixed tile size, margin, spacing | Standard tilesets, consistent tile sizes |
| **Collection-based** | Each tile is separate image file                   | Variable-size tiles, sprites as tiles    |

### Layer Types

| Layer            | Purpose                                                | Phaser Access          |
| ---------------- | ------------------------------------------------------ | ---------------------- |
| **Tile Layer**   | Grid-based tile storage with flip flags                | `map.createLayer()`    |
| **Object Layer** | Free-positioned shapes, points, polygons, tile objects | `map.getObjectLayer()` |
| **Image Layer**  | Background/foreground images with repeat               | `map.images` array     |
| **Group Layer**  | Hierarchical organization                              | Flattened on export    |

### Recommended Layer Structure (Top to Bottom in Tiled)

```
Foreground      (renders above player, depth: 10+)
├── Trees-Top
├── Roof-Tops
Objects         (spawn points, triggers, collision zones)
├── Enemies
├── Collectibles
├── Triggers
Player-Ref      (reference layer, not exported)
Ground          (main collision layer)
├── Platforms
├── Walls
Background      (decoration, no collision)
├── Decorations
├── Parallax-Far
├── Parallax-Near
```

---

## Global Tile IDs (GIDs)

Critical concept for understanding tilemap data.

- **GID 0** = Empty tile
- **GID 1+** = References tiles across all tilesets
- Each tileset has a `firstgid` — the GID of its first tile
- **Local ID** = GID - tileset.firstgid

### Flip Flags (Stored in High Bits)

```javascript
const FLIPPED_HORIZONTALLY = 0x80000000;
const FLIPPED_VERTICALLY = 0x40000000;
const FLIPPED_DIAGONALLY = 0x20000000;

function parseGID(rawGid) {
  const flipH = (rawGid & FLIPPED_HORIZONTALLY) !== 0;
  const flipV = (rawGid & FLIPPED_VERTICALLY) !== 0;
  const flipD = (rawGid & FLIPPED_DIAGONALLY) !== 0;
  const gid = rawGid & ~0xf0000000;
  return { gid, flipH, flipV, flipD };
}
```

---

## Loading Tilemaps in Phaser

```javascript
preload() {
  // Load tilemap JSON (exported from Tiled)
  this.load.tilemapTiledJSON('level1', 'assets/tilemaps/level1.json');

  // Load tileset image(s)
  this.load.image('terrain', 'assets/tilesets/terrain.png');
  this.load.image('props', 'assets/tilesets/props.png');
}
```

### Extruded Tilesets (Prevent Bleeding)

When tiles show thin lines between them, use extruded tilesets:

```javascript
// Tileset extruded by 1px
// margin: 1, spacing: 2 (2 * extrusion)
const tileset = map.addTilesetImage('tileset-name', 'tiles', 16, 16, 1, 2);
```

---

## Creating the Map

```javascript
create() {
  const map = this.make.tilemap({ key: 'level1' });

  // Name MUST match Tiled tileset name exactly
  const tileset = map.addTilesetImage('tileset-name-in-tiled', 'tiles');

  // Layer names MUST match Tiled layer names
  const bgLayer = map.createLayer('Background', tileset, 0, 0);
  const groundLayer = map.createLayer('Ground', tileset, 0, 0);
  const fgLayer = map.createLayer('Foreground', tileset, 0, 0);

  bgLayer.setDepth(0);
  groundLayer.setDepth(5);
  fgLayer.setDepth(10);  // Renders above player
}
```

### Multiple Tilesets Per Layer

```javascript
const groundLayer = map.createLayer('Ground', [terrainTileset, propsTileset, decorTileset]);
```

---

## Collision Setup

### By Custom Property (Recommended)

Set `collides: true` on tiles in Tiled's Tileset Editor:

```javascript
groundLayer.setCollisionByProperty({ collides: true });
```

### By Tile Index

```javascript
groundLayer.setCollision([1, 2, 3]);
groundLayer.setCollisionBetween(1, 100);
groundLayer.setCollisionByExclusion([-1, 0]);
```

### One-Way Platforms

```javascript
groundLayer.forEachTile((tile) => {
  if (tile.properties.oneWay) {
    tile.collideDown = false;
    tile.collideLeft = false;
    tile.collideRight = false;
  }
});
```

### Physics Collider

```javascript
this.physics.add.collider(player, groundLayer);
this.physics.add.collider(player, hazardLayer, this.onHazardHit, null, this);

onHazardHit(player, tile) {
  player.damage(tile.properties.damage || 10);
}
```

---

## Object Layers

### Reading Objects

```javascript
const objectLayer = map.getObjectLayer('Objects');

// Find by name
const spawnPoint = map.findObject('Objects', (obj) => obj.name === 'PlayerSpawn');
player.setPosition(spawnPoint.x, spawnPoint.y);

// Filter by type
const enemies = map.filterObjects('Enemies', (obj) => obj.type === 'goblin');
```

### Accessing Custom Properties

Properties are stored as array of `{name, type, value}`:

```javascript
function getProperty(obj, propName) {
  if (!obj.properties) return undefined;
  const prop = obj.properties.find((p) => p.name === propName);
  return prop ? prop.value : undefined;
}

const isLocked = getProperty(door, 'locked');
const damage = getProperty(trap, 'damage');
```

### Creating Sprites from Objects

```javascript
const coins = map.createFromObjects('Collectibles', {
  name: 'coin',
  key: 'coin',
  classType: Phaser.Physics.Arcade.Sprite
});

coins.forEach((coin) => {
  this.physics.add.existing(coin);
  coin.body.setAllowGravity(false);
});
```

---

## Tile Manipulation

```javascript
// Get tile
const tile = groundLayer.getTileAtWorldXY(pointer.worldX, pointer.worldY);
const tile = groundLayer.getTileAt(tileX, tileY);

// Place/remove
groundLayer.putTileAt(tileIndex, tileX, tileY);
groundLayer.removeTileAt(tileX, tileY);

// Fill area
groundLayer.fill(tileIndex, startX, startY, width, height);

// Weighted randomize
groundLayer.weightedRandomize(x, y, width, height, [
  { index: 1, weight: 10 },
  { index: 2, weight: 3 },
  { index: 3, weight: 1 }
]);

// Iterate all tiles
groundLayer.forEachTile((tile) => {
  if (tile.properties.spawnEnemy) {
    spawnEnemy(tile.getCenterX(), tile.getCenterY());
    groundLayer.removeTileAt(tile.x, tile.y);
  }
});
```

---

## Camera and World Bounds

```javascript
// Set world/camera bounds to map size
this.physics.world.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
this.cameras.main.setBounds(0, 0, map.widthInPixels, map.heightInPixels);

// Follow player with smoothing
this.cameras.main.startFollow(player, true, 0.1, 0.1);

// Prevent tile seams at fractional positions
this.cameras.main.roundPixels = true;
```

---

## Parallax Scrolling

### In Tiled

Set `parallaxx`/`parallaxy` on layers: `0.5` = half speed, `0.0` = fixed, `1.5` = faster.

### In Phaser

```javascript
skyLayer.setScrollFactor(0);          // Fixed background
cloudsLayer.setScrollFactor(0.2);
groundLayer.setScrollFactor(1);       // Normal (default)

// TileSprite for infinite repeating background
const bg = this.add.tileSprite(0, 0, this.cameras.main.width, this.cameras.main.height, 'background');
bg.setOrigin(0, 0).setScrollFactor(0);

update() {
  bg.tilePositionX = this.cameras.main.scrollX * 0.3;
}
```

---

## Debugging Tilemaps

```javascript
// Visualize collision tiles
const debugGraphics = this.add.graphics();
groundLayer.renderDebug(debugGraphics, {
  tileColor: null,
  collidingTileColor: new Phaser.Display.Color(243, 134, 48, 200),
  faceColor: new Phaser.Display.Color(40, 39, 37, 255)
});

// Log tile on click
this.input.on('pointerdown', (pointer) => {
  const worldPoint = this.cameras.main.getWorldPoint(pointer.x, pointer.y);
  const tile = groundLayer.getTileAtWorldXY(worldPoint.x, worldPoint.y);
  if (tile) console.log('Tile:', tile.index, tile.properties);
});
```

---

## Performance Tips

1. Use static layers when tiles don't change
2. Phaser auto-culls off-screen tiles — verify with large maps
3. Merge purely visual layers to reduce layer count
4. Use texture atlas for tileset images
5. Pool sprites created from object layers
6. Set `layer.setCullPadding(2, 2)` for large worlds

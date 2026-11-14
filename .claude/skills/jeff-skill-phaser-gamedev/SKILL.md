---
name: jeff-skill-phaser-gamedev
description: Build 2D browser games with Phaser 4. Use for scene architecture, physics (Arcade/Matter), spritesheet loading, tilemap integration, input handling, animations, filters, and performance optimization, and to upgrade a Phaser 3 project to Phaser 4. Covers TypeScript patterns and common pitfalls.
---

# Phaser 4 Game Development

Targets Phaser 4 (latest 4.x; 4.2.1 as of November 2026 — check `npm view phaser version`).

**Phaser's own API skills ship inside the package**, versioned with the installed release:
`node_modules/phaser/skills/<topic>/SKILL.md` — `scenes`, `game-setup-and-config`, `physics-arcade`, `physics-matter`,
`tilemaps`, `sprites-and-images`, `animations`, `filters-and-postfx`, `render-textures`, `particles`, `cameras`,
`v4-new-features` and more (`ls node_modules/phaser/skills`). Read the matching one before using an API you're not sure
of; it beats recalling the API from memory.

**Project still on Phaser 3?** Upgrade before any other work: `npm install phaser@4`, then follow the official
[v3 to v4 migration guide](https://github.com/phaserjs/phaser/blob/master/changelog/v4/4.0/MIGRATION-GUIDE.md) (also
shipped as `node_modules/phaser/skills/v3-to-v4-migration/SKILL.md`) and work through its checklist.

## v4 APIs That Differ From What You Remember

| Don't write (removed)                                                      | Write                                                                                             |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `preFX` / `postFX`, `BitmapMask`, `setMask()`                              | Filters: `obj.filters.internal` / `.external`, e.g. `sprite.filters.internal.addMask(maskObject)` |
| `sprite.setTintFill(color)`                                                | `sprite.setTint(color).setTintMode(Phaser.TintModes.FILL)`                                        |
| `sprite.setPipeline('Light2D')`                                            | `sprite.setLighting(true)`; lights take an explicit `z` height                                    |
| Custom WebGL pipelines, raw `gl` calls                                     | Render nodes (`RenderConfig#renderNodes`); an `Extern` object for raw WebGL                       |
| Drawing to a `DynamicTexture`/`RenderTexture` and expecting it immediately | Queue the draws, then call `render()`                                                             |
| `Phaser.Geom.Point`                                                        | `Phaser.Math.Vector2` (all `Geom` helpers return `Vector2`)                                       |
| `Phaser.Math.TAU` as π/2, `Phaser.Math.PI2`                                | `Phaser.Math.TAU` is now 2π; use `Phaser.Math.PI_OVER_2` for π/2                                  |
| `Phaser.Struct.Set` / `Phaser.Struct.Map`                                  | Native `Set` / `Map`                                                                              |
| `Mesh`, `Plane`, `Create.GenerateTexture`                                  | Removed — no replacement                                                                          |

- `setTintFill()` still exists as a do-nothing stub: it type-checks, takes no arguments and has no effect. A sprite that
  won't tint is usually this.
- `roundPixels` now defaults to `false`; set it for pixel art (per object: `vertexRoundMode`).
- WebGL is the target. The Canvas renderer is deprecated and lacks v4's filters and lighting — keep `type: Phaser.AUTO`.

## STOP: Before Loading Any Spritesheet

**Read [spritesheets-nineslice.md](references/spritesheets-nineslice.md) FIRST.**

Spritesheet loading is fragile—a few pixels off causes silent corruption that compounds into broken visuals. The reference file contains the mandatory inspection protocol.

**Quick rules** (details in reference):

1. **Measure the asset** before writing loader code—never guess frame dimensions
2. **Character sprites use SQUARE frames**: If you calculate frameWidth=56, try 56 for height first
3. **Different animations have different frame sizes**: A run cycle needs wider frames than idle; an attack needs extra width for weapon swing. Measure EACH spritesheet independently
4. **Check for spacing**: Gaps between frames require `spacing: N` in loader config
5. **Verify the math**: `imageWidth = (frameWidth × cols) + (spacing × (cols - 1)) + (margin × 2)`

---

## Reference Files

Read these BEFORE working on the relevant feature:

| When working on...                 | Read first                                                        |
| ---------------------------------- | ----------------------------------------------------------------- |
| Loading ANY spritesheet            | [spritesheets-nineslice.md](references/spritesheets-nineslice.md) |
| Nine-slice UI panels               | [spritesheets-nineslice.md](references/spritesheets-nineslice.md) |
| Tiled tilemaps, collision layers   | [tilemaps.md](references/tilemaps.md)                             |
| Physics tuning, groups, pooling    | [arcade-physics.md](references/arcade-physics.md)                 |
| Performance issues, object pooling | [performance.md](references/performance.md)                       |

---

## Architecture Decisions (Make Early)

### Physics System Choice

| System     | Use When                                                               |
| ---------- | ---------------------------------------------------------------------- |
| **Arcade** | Platformers, shooters, most 2D games. Fast AABB collisions             |
| **Matter** | Physics puzzles, ragdolls, realistic collisions. Slower, more accurate |
| **None**   | Menu scenes, visual novels, card games                                 |

### Scene Structure

```
scenes/
├── BootScene.ts      # Asset loading, progress bar
├── MenuScene.ts      # Title screen, options
├── GameScene.ts      # Main gameplay
├── UIScene.ts        # HUD overlay (launched parallel)
└── GameOverScene.ts  # End screen, restart
```

### Scene Transitions

```typescript
this.scene.start('GameScene', { level: 1 }); // Stop current, start new
this.scene.launch('UIScene'); // Run in parallel
this.scene.pause('GameScene'); // Pause
this.scene.stop('UIScene'); // Stop
```

---

## Core Patterns

### Game Configuration

```typescript
const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: 800,
  height: 600,
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH
  },
  physics: {
    default: 'arcade',
    arcade: { gravity: { y: 300 }, debug: false }
  },
  scene: [BootScene, MenuScene, GameScene]
};
```

### Scene Lifecycle

```typescript
class GameScene extends Phaser.Scene {
  init(data: { level: number }): void {} // Receive data from previous scene
  preload(): void {} // Load assets (runs before create)
  create(): void {} // Set up game objects, physics, input — once
  update(time: number, delta: number): void {} // Game loop; use delta for frame-rate independence
}
```

### Frame-Rate Independent Movement

```typescript
// CORRECT: scales with frame rate
this.player.x += this.speed * (delta / 1000);

// WRONG: varies with frame rate
this.player.x += this.speed;
```

---

## Anti-Patterns

| Anti-Pattern                 | Problem                          | Solution                            |
| ---------------------------- | -------------------------------- | ----------------------------------- |
| Global state on `window`     | Scene transitions break state    | Use scene data, registries          |
| Loading in `create()`        | Assets not ready when referenced | Load in `preload()`, use Boot scene |
| Frame counting               | Game speed varies with FPS       | Use `delta / 1000`                  |
| Matter for simple collisions | Unnecessary complexity           | Arcade handles most 2D games        |
| One giant scene              | Hard to extend                   | Separate gameplay/UI/menus          |
| Magic numbers                | Impossible to balance            | Config objects, constants           |
| No object pooling            | GC stutters                      | Groups with `setActive(false)`      |

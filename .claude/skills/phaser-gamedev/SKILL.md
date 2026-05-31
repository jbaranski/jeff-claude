---
name: phaser-gamedev
description: Build 2D browser games with Phaser 3. Covers scene architecture, physics (Arcade/Matter), spritesheets, tilemaps, input, animations, and performance optimization. Use when developing Phaser 3 games, setting up game scenes, integrating physics, loading spritesheets/tilemaps, or optimizing game performance.
---

# Phaser Game Development Guide

This skill covers building 2D browser games with Phaser 3.

## Before You Start

**Read the spritesheet reference first** (`references/spritesheets-nineslice.md`). Spritesheet loading is fragile—a few pixels off causes silent corruption that compounds into broken visuals. Measure assets before writing any loader code.

## Architecture Planning

Establish these before writing code:

1. **Scenes** — Which scenes are needed? (Boot, Menu, Game, UI, GameOver)
2. **Entities** — What are the core game objects and how do they interact?
3. **Physics** — Arcade (fast AABB, most games), Matter (realistic/complex), or None (UI-only scenes)
4. **Input** — Keyboard, pointer, or both?

## Core Philosophy

- Scene-first architecture: organize code around scene lifecycles
- Composition over inheritance for game entities
- Make physics decisions early—changing physics systems later is painful
- "Phaser provides powerful primitives—scenes, sprites, physics, input—but architecture is your responsibility"

## Common Pitfalls

| Avoid | Use Instead |
|-------|------------|
| Global `window` state | Scene data registry or event emitter |
| Loading assets in `create()` | Load in `preload()` |
| Frame counting for timing | Delta-time calculations |
| Monolithic scene classes | Modular systems, scene boundaries |

## Reference Materials

See the `references/` directory for detailed guides:

- **core-patterns.md** — Game config, scene lifecycle, game objects, input, animations, asset loading
- **spritesheets-nineslice.md** — Spritesheet loading, nine-slice UI panels, debugging visuals
- **arcade-physics.md** — Arcade physics deep dive: bodies, groups, colliders, movement patterns
- **tilemaps.md** — Tiled integration, collision setup, object layers, tile manipulation
- **performance.md** — 60fps optimization: object pooling, texture atlases, culling, update loop best practices

## Tailoring Your Approach

Adjust based on:
- **Game genre** — platformer vs. top-down vs. puzzle
- **Target platform** — mobile (touch input, fewer particles) vs. desktop
- **Visual style** — pixel art (integer scaling, `roundPixels: true`) vs. smooth assets
- **Entity count** — object pooling becomes critical above ~50 dynamic objects

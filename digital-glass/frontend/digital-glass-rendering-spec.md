# Digital Glass UI Rendering Spec v0.1

> This specification dictates how the `OVERLAY_RENDER` stream is translated into deterministic visual elements on the screen. It prevents UI collisions, defines animation curves, and enforces a strict z-index hierarchy.

## 1. The Grid (Layout Zones)

The screen is divided into discrete, non-overlapping zones. Overlays must declare their zone and cannot overflow.

```text
+--------------------------------------------------+
| [Zone A: Upper Left]        [Zone B: Upper Right]|
|                                                  |
|                                                  |
|                                                  |
|                                                  |
| [Zone C: Lower Left]        [Zone D: Lower Right]|
|                   [Zone E: Center Bottom]        |
+--------------------------------------------------+
```

### Overlay Mapping to Zones
- **`RIVALRY_BADGE`**: Zone A (Upper Left)
- **`SHOT_CONTEXT`**: Zone E (Center Bottom)
- **`MOMENTUM_SPIKE`**: Zone B (Upper Right)
- **`EDGE_INDICATOR`**: Zone C or D (Lower Sides)
- **`CLOSING_PRESSURE`**: Zone E (Center Bottom, overrides SHOT_CONTEXT)

---

## 2. Animation & Timing (The Feel)

Overlays must not "pop" in. They follow strict easing curves to feel broadcast-quality.

### Curves
- **Entrance Easing**: `cubic-bezier(0.16, 1, 0.3, 1)` (Swift out, slow in)
- **Exit Easing**: `cubic-bezier(0.7, 0, 0.84, 0)` (Slow out, swift in)

### Durations
- **Entrance**: `400ms`
- **Exit**: `300ms`
- **Attention Pulse (optional)**: `1200ms` infinite loop (e.g., glowing border on high priority)

### Lifecycle Events
1. `onEnter`: `opacity: 0 -> 1`, `transform: translateY(20px) -> translateY(0)`
2. `onHold`: Remains visible for `ttl_ms` from the payload (typically 3000ms - 6000ms).
3. `onExit`: `opacity: 1 -> 0`, `transform: translateY(0) -> translateY(-10px)`

---

## 3. Stacking & Z-Index Hierarchy

When overlays conflict, priority decides. The UI engine handles preemption.

**Z-Index Tiers:**
- `100`: Base video/canvas layer
- `200`: Ambient overlays (`EDGE_INDICATOR`)
- `300`: Standard context (`SHOT_CONTEXT`, `RIVALRY_BADGE`)
- `400`: High-impact events (`MOMENTUM_SPIKE`)
- `500`: Critical alerts (`CLOSING_PRESSURE`)

### Conflict Resolution (Preemption)
If a new overlay arrives for a zone that is currently occupied:
1. **Compare Priorities**: If `new_priority > current_priority + 0.1`, evict current immediately (trigger `onExit`).
2. **Same Priority**: Respect the current overlay's TTL. Drop the new one or queue it if TTL < 1500ms remaining.
3. **`CLOSING_PRESSURE` Rule**: Unconditionally clears Zone E and suppresses other non-critical overlays.

---

## 4. React Implementation (The UI Engine)

The frontend uses a master `OverlayContainer` that subscribes to the stream and routes components to zones.

```tsx
// overlay-manager.tsx
import React, { useState, useEffect } from 'react';
import { useGlassStream } from './use-glass-stream';
import { AnimatePresence, motion } from 'framer-motion';

export const OverlayManager = () => {
  const { currentEvent } = useGlassStream({ /* ... */ });
  const [activeOverlays, setActiveOverlays] = useState<Record<string, Overlay>>({});

  useEffect(() => {
    if (currentEvent?.type === 'OVERLAY_RENDER') {
      const newOverlays = currentEvent.overlays;

      setActiveOverlays(current => {
         const next = { ...current };
         newOverlays.forEach(overlay => {
             // 1. Check Zone conflicts
             const zone = getZoneForType(overlay.type);
             const existing = getOverlayInZone(next, zone);

             // 2. Resolve Preemption
             if (!existing || overlay.priority > existing.priority) {
                 next[overlay.overlay_id] = overlay;
             }
         });
         return next;
      });
    }
  }, [currentEvent]);

  // 3. TTL Cleanup Loop
  useEffect(() => {
    const interval = setInterval(() => {
       const now = Date.now();
       setActiveOverlays(current => {
           // Filter out expired overlays based on created_at + ttl_ms
           // ...
       });
    }, 100);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="absolute inset-0 pointer-events-none">
       {/* Zone A: Top Left */}
       <div className="absolute top-8 left-8">
         <AnimatePresence>
            {/* Render RIVALRY_BADGE */}
         </AnimatePresence>
       </div>

       {/* Zone E: Bottom Center */}
       <div className="absolute bottom-12 left-1/2 -translate-x-1/2">
         <AnimatePresence>
            {/* Render SHOT_CONTEXT or CLOSING_PRESSURE */}
         </AnimatePresence>
       </div>
    </div>
  );
}
```

## 5. Summary

This spec guarantees that the mathematical rigor of the backend Decision Engine is respected visually. No screen clutter, predictable animations, and a broadcast-grade feel out of the box.

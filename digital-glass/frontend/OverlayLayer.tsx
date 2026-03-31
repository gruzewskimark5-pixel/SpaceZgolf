import React, { useEffect, useMemo, useState } from "react";

export type OverlayType =
  | "RIVALRY_BADGE"
  | "SHOT_CONTEXT"
  | "EDGE_INDICATOR"
  | "MOMENTUM_SPIKE"
  | "CLOSING_PRESSURE";

export interface Overlay {
  overlay_id: string;
  type: OverlayType;
  players: string[];
  priority: number;
  ttl_ms: number;
  payload: any;
  reason: string;
  created_at: string;
}

export interface OverlayRenderProps {
  overlays: Overlay[];
}

type Zone = "TL" | "TR" | "BC" | "MB";

const OVERLAY_ZONE: Record<OverlayType, Zone> = {
  RIVALRY_BADGE: "TL",
  SHOT_CONTEXT: "BC",
  EDGE_INDICATOR: "TR",
  MOMENTUM_SPIKE: "MB",
  CLOSING_PRESSURE: "MB",
};

function useTimedOverlay(overlay: Overlay | null) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!overlay) return;

    setVisible(true);

    const fadeOutTime = overlay.ttl_ms - 200;

    const fadeTimer = setTimeout(() => setVisible(false), fadeOutTime);
    const removeTimer = setTimeout(() => setVisible(false), overlay.ttl_ms);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(removeTimer);
    };
  }, [overlay?.overlay_id, overlay?.ttl_ms]);

  return visible;
}

// Mock placeholder components for rendering payloads
const RivalryBadge = (props: any) => <div>RivalryBadge: {JSON.stringify(props)}</div>;
const ShotContext = (props: any) => <div>ShotContext: {JSON.stringify(props)}</div>;
const EdgeIndicator = (props: any) => <div>EdgeIndicator: {JSON.stringify(props)}</div>;
const MomentumSpike = (props: any) => <div>MomentumSpike: {JSON.stringify(props)}</div>;
const ClosingPressure = (props: any) => <div>ClosingPressure: {JSON.stringify(props)}</div>;

function renderOverlay(overlay: Overlay) {
  switch (overlay.type) {
    case "RIVALRY_BADGE": return <RivalryBadge {...overlay.payload} />;
    case "SHOT_CONTEXT": return <ShotContext {...overlay.payload} />;
    case "EDGE_INDICATOR": return <EdgeIndicator {...overlay.payload} />;
    case "MOMENTUM_SPIKE": return <MomentumSpike {...overlay.payload} />;
    case "CLOSING_PRESSURE": return <ClosingPressure {...overlay.payload} />;
    default: return null;
  }
}

function ZoneRenderer({ overlay }: { overlay: Overlay | null }) {
  const visible = useTimedOverlay(overlay);

  if (!overlay) return null;

  return (
    <div className={`transition-opacity duration-200 ${visible ? "opacity-100" : "opacity-0"}`}>
      {renderOverlay(overlay)}
    </div>
  );
}

export function OverlayLayer({ overlays }: OverlayRenderProps) {
  const zones = useMemo(() => {
    const grouped: Record<Zone, Overlay[]> = {
      TL: [],
      TR: [],
      BC: [],
      MB: [],
    };

    overlays.forEach((o) => {
      grouped[OVERLAY_ZONE[o.type]].push(o);
    });

    const pickTop = (list: Overlay[]) =>
      list.sort((a, b) => b.priority - a.priority)[0] || null;

    return {
      TL: pickTop(grouped.TL),
      TR: pickTop(grouped.TR),
      BC: pickTop(grouped.BC),
      MB: pickTop(grouped.MB),
    };
  }, [overlays]);

  return (
    <div className="pointer-events-none fixed inset-0">
      {/* Top Left */}
      <div className="absolute top-4 left-4">
        <ZoneRenderer overlay={zones.TL} />
      </div>

      {/* Top Right */}
      <div className="absolute top-4 right-4">
        <ZoneRenderer overlay={zones.TR} />
      </div>

      {/* Middle Bottom */}
      <div className="absolute bottom-24 left-1/2 -translate-x-1/2">
        <ZoneRenderer overlay={zones.MB} />
      </div>

      {/* Bottom Center */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
        <ZoneRenderer overlay={zones.BC} />
      </div>
    </div>
  );
}

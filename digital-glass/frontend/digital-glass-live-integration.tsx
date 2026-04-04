import React, { useState } from 'react';
import { useGlassStream } from './use-glass-stream';
import { GlassEvent } from './glass-websocket-types';

// Mock components
const StatePane = ({ event }: { event: GlassEvent }) => <div>StatePane</div>;
const CausalityPane = ({ event }: { event: GlassEvent }) => <div>CausalityPane</div>;
const OutcomePane = ({ event }: { event: GlassEvent }) => <div>OutcomePane</div>;

export const DigitalGlass = () => {
  const authToken = 'mock_token'; // Replace with actual token

  const { currentEvent, eventHistory, status, error } = useGlassStream({
    url: 'wss://glass.spacezgolf.com/stream',
    token: authToken,
    subscription: {
      view: 'digital_glass',
      athlete_id: 'athlete123',
      hole_id: 'miakka_7'
    }
  });

  const [historyIndex, setHistoryIndex] = useState(0);

  const displayEvent = eventHistory[historyIndex] || currentEvent;

  return (
    <div className="flex flex-col h-screen">
      <div className="flex justify-between p-4 bg-gray-800 text-white">
        <h2>Digital Glass Stream</h2>
        <div>
          Status: {status}
          {status === 'connected' && <span className="ml-2 w-3 h-3 bg-green-500 rounded-full inline-block animate-pulse" />}
        </div>
      </div>

      {error && <div className="p-4 bg-red-500 text-white">{error}</div>}

      <div className="flex-1 overflow-auto p-4 flex gap-4">
        {displayEvent ? (
          <>
            <div className="w-1/3 border p-4">
              <StatePane event={displayEvent} />
            </div>
            <div className="w-1/3 border p-4">
              <CausalityPane event={displayEvent} />
            </div>
            <div className="w-1/3 border p-4">
              <OutcomePane event={displayEvent} />
            </div>
          </>
        ) : (
          <div>Waiting for events...</div>
        )}
      </div>

      <div className="flex gap-4 p-4 border-t">
        <button
          disabled={historyIndex >= eventHistory.length - 1}
          onClick={() => setHistoryIndex(i => i + 1)}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-400"
        >
          Previous Event
        </button>
        <button
          disabled={historyIndex === 0}
          onClick={() => setHistoryIndex(i => Math.max(0, i - 1))}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-400"
        >
          Next Event
        </button>
      </div>
    </div>
  );
};

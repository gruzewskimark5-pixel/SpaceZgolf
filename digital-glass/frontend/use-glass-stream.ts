import { useState, useEffect, useRef, useCallback } from 'react';
import { GlassEvent, ServerMessage } from './glass-websocket-types';

interface UseGlassStreamParams {
  url: string;
  token: string;
  subscription: {
    view: string;
    athlete_id?: string;
    hole_id?: string;
  };
}

export function useGlassStream({ url, token, subscription }: UseGlassStreamParams) {
  const [currentEvent, setCurrentEvent] = useState<GlassEvent | null>(null);
  const [eventHistory, setEventHistory] = useState<GlassEvent[]>([]);
  const [status, setStatus] = useState<'connecting' | 'connected' | 'reconnecting' | 'disconnected'>('disconnected');
  const [error, setError] = useState<string | null>(null);

  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout>();
  const heartbeatTimeout = useRef<NodeJS.Timeout>();
  const reconnectAttempts = useRef(0);

  const maxReconnectDelay = 30000;
  const heartbeatInterval = 15000;

  const connect = useCallback(() => {
    try {
      setStatus(reconnectAttempts.current > 0 ? 'reconnecting' : 'connecting');
      ws.current = new WebSocket(`${url}?token=${token}`);

      ws.current.onopen = () => {
        setStatus('connected');
        setError(null);
        reconnectAttempts.current = 0;

        ws.current?.send(JSON.stringify({
          type: 'subscribe',
          ...subscription
        }));

        resetHeartbeat();
      };

      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data) as ServerMessage;

        switch (data.type) {
          case 'event':
            setCurrentEvent(data.event);
            setEventHistory(prev => {
                const newHistory = [data.event, ...prev];
                if (newHistory.length > 100) return newHistory.slice(0, 100);
                return newHistory;
            });
            break;
          case 'heartbeat':
            resetHeartbeat();
            break;
          case 'error':
            setError(data.message);
            break;
        }
      };

      ws.current.onclose = () => {
        setStatus('disconnected');
        handleReconnect();
      };

      ws.current.onerror = () => {
        // ws.onerror doesn't provide useful info, handle in onclose
      };

    } catch (err) {
      setError('Failed to establish connection');
      handleReconnect();
    }
  }, [url, token, subscription]);

  const resetHeartbeat = () => {
    if (heartbeatTimeout.current) clearTimeout(heartbeatTimeout.current);
    heartbeatTimeout.current = setTimeout(() => {
      // Missed heartbeat
      ws.current?.close();
    }, heartbeatInterval);
  };

  const handleReconnect = () => {
    if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);

    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), maxReconnectDelay);
    reconnectAttempts.current += 1;

    reconnectTimeout.current = setTimeout(connect, delay);
  };

  useEffect(() => {
    connect();

    return () => {
      if (ws.current) ws.current.close();
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      if (heartbeatTimeout.current) clearTimeout(heartbeatTimeout.current);
    };
  }, [connect]);

  return {
    currentEvent,
    eventHistory,
    status,
    error
  };
}

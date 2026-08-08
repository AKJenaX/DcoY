import { useState, useEffect, useRef } from "react";
import { api } from "../services/api";

export type ConnectionStatus = "connecting" | "connected" | "reconnecting" | "polling" | "disconnected";

export function useRealtimeChannel(channel: string) {
  const [data, setData] = useState<any>(channel === "telemetry" || channel === "geolocation" ? [] : null);
  const [status, setStatus] = useState<ConnectionStatus>("connecting");
  const [error, setError] = useState<string | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxRetries = 3;
  const pollIntervalRef = useRef<any>(null);
  const isPollingRef = useRef(false);

  // Helper to trigger polling fallback
  const startPollingFallback = () => {
    if (isPollingRef.current) return;
    isPollingRef.current = true;
    setStatus("polling");
    
    const runPoll = async () => {
      try {
        if (channel === "telemetry") {
          const res = await api.getDetectLogs();
          setData(res.events || []);
        } else if (channel === "geolocation") {
          const res = await api.getDetectLogs();
          const uniqueGeos: any[] = [];
          const seenIps = new Set();
          (res.events || []).forEach((evt: any) => {
            const loc = evt.location;
            if (loc && loc.ip && !seenIps.has(loc.ip)) {
              seenIps.add(loc.ip);
              uniqueGeos.push(loc);
            }
          });
          setData(uniqueGeos);
        } else if (channel === "simulation") {
          const res = await api.getSimulations();
          if (res && res.length > 0) {
            const latest = res[0];
            setData({
              run_id: latest.id,
              scenario_name: latest.scenario_name,
              status: latest.status.toLowerCase(),
              step: latest.scanned_events_count,
              total_steps: latest.scanned_events_count,
              results: latest.results_data ? JSON.parse(latest.results_data) : null
            });
          }
        }
        setError(null);
      } catch (err: any) {
        setError(err.message || "Failed to poll data fallback.");
      }
    };

    runPoll();
    pollIntervalRef.current = setInterval(runPoll, 4000);
  };

  const stopPollingFallback = () => {
    isPollingRef.current = false;
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  };

  useEffect(() => {
    let active = true;
    reconnectAttemptsRef.current = 0;

    const token = localStorage.getItem("auth_token");
    if (!token) {
      setStatus("disconnected");
      return;
    }

    // Pre-fetch existing telemetry logs on mount
    const fetchInitial = async () => {
      try {
        if (channel === "telemetry") {
          const res = await api.getDetectLogs();
          const eventsList = res.data || res.events || [];
          if (Array.isArray(eventsList) && eventsList.length > 0 && active) {
            setData(eventsList);
          }
        }
      } catch (e) {
        console.warn("Initial telemetry pre-fetch notice:", e);
      }
    };
    fetchInitial();

    const connectWebSocket = () => {
      if (!active) return;
      
      const token = localStorage.getItem("auth_token") || "";
      const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsHost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" 
        ? "localhost:8001" 
        : window.location.host;
      
      const wsUrl = `${wsProtocol}//${wsHost}/ws/${channel}?token=${token}`;
      
      setStatus(reconnectAttemptsRef.current > 0 ? "reconnecting" : "connecting");
      
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        if (!active) {
          ws.close();
          return;
        }
        setStatus("connected");
        setError(null);
        reconnectAttemptsRef.current = 0;
        stopPollingFallback();
      };

      ws.onmessage = (event) => {
        if (!active) return;
        try {
          const messageData = JSON.parse(event.data);
          
          if (channel === "telemetry") {
            setData((prev: any[]) => {
              const list = Array.isArray(prev) ? prev : [];
              // Filter duplicates if any
              const filtered = list.filter(item => item.timestamp !== messageData.timestamp);
              const updated = [messageData, ...filtered];
              return updated.slice(0, 200); // cap at 200 events
            });
          } else if (channel === "geolocation") {
            setData((prev: any[]) => {
              const list = Array.isArray(prev) ? prev : [];
              const index = list.findIndex(loc => loc.ip === messageData.ip);
              if (index >= 0) {
                const updated = [...list];
                updated[index] = messageData;
                return updated;
              } else {
                return [...list, messageData];
              }
            });
          } else if (channel === "simulation") {
            setData(messageData);
          }
        } catch (err) {
          console.error("Error parsing WebSocket message:", err);
        }
      };

      ws.onerror = () => {
        // Will close and trigger reconnect/fallback in onclose
      };

      ws.onclose = (event) => {
        if (!active) return;
        socketRef.current = null;
        
        if (event.code === 4003) {
          setStatus("disconnected");
          setError("WebSocket unauthorized. Please log in again.");
          startPollingFallback();
          return;
        }

        if (reconnectAttemptsRef.current < maxRetries) {
          const timeout = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 8000);
          reconnectAttemptsRef.current += 1;
          setTimeout(() => {
            if (active) connectWebSocket();
          }, timeout);
        } else {
          setError("WebSocket connection lost. Using fallback HTTP polling.");
          startPollingFallback();
        }
      };
    };

    // Prefill data first
    const prefillData = async () => {
      try {
        if (channel === "telemetry") {
          const res = await api.getDetectLogs();
          if (active) setData(res.events || []);
        } else if (channel === "geolocation") {
          const res = await api.getDetectLogs();
          const uniqueGeos: any[] = [];
          const seenIps = new Set();
          (res.events || []).forEach((evt: any) => {
            const loc = evt.location;
            if (loc && loc.ip && !seenIps.has(loc.ip)) {
              seenIps.add(loc.ip);
              uniqueGeos.push(loc);
            }
          });
          if (active) setData(uniqueGeos);
        } else if (channel === "simulation") {
          const res = await api.getSimulations();
          if (active && res && res.length > 0) {
            const latest = res[0];
            setData({
              run_id: latest.id,
              scenario_name: latest.scenario_name,
              status: latest.status.toLowerCase(),
              step: latest.scanned_events_count,
              total_steps: latest.scanned_events_count,
              results: latest.results_data ? JSON.parse(latest.results_data) : null
            });
          }
        }
      } catch (e) {
        console.warn("Failed to prefill data, opening WebSocket directly", e);
      }
      
      connectWebSocket();
    };

    prefillData();

    return () => {
      active = false;
      stopPollingFallback();
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [channel]);

  return { data, status, error };
}

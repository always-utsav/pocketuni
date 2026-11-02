/**
 * PocketUni WebSocket Realtime Client
 * Connects to /api/v1/ws and dispatches real-time events for applications,
 * announcements, and faculty profile updates.
 */

type RealtimeEventHandler = (data: any) => void;

class RealtimeClient {
  private ws: WebSocket | null = null;
  private handlers: Map<string, Set<RealtimeEventHandler>> = new Map();
  private reconnectTimeout: any = null;
  private pingInterval: any = null;
  private isExplicitlyClosed: boolean = false;
  private token: string | null = null;

  public connect(token: string) {
    this.token = token;
    this.isExplicitlyClosed = false;

    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Fallback to localhost:8000 if running in vite dev port (e.g. 5173 or 3000)
    const host = window.location.port === '8000' ? window.location.host : 'localhost:8000';
    const wsUrl = `${wsProtocol}//${host}/api/v1/ws?token=${encodeURIComponent(token)}`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('[Realtime WS] Connected successfully.');
        this.startHeartbeat();
      };

      this.ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const type = payload.type || payload.event;
          if (!type) return;

          // Dispatch to specific event handlers
          const specificHandlers = this.handlers.get(type);
          if (specificHandlers) {
            specificHandlers.forEach(h => h(payload.data || payload));
          }

          // Dispatch to wildcard handlers
          const wildcardHandlers = this.handlers.get('*');
          if (wildcardHandlers) {
            wildcardHandlers.forEach(h => h(payload));
          }
        } catch (e) {
          console.warn('[Realtime WS] Failed to parse message:', event.data);
        }
      };

      this.ws.onerror = (err) => {
        console.warn('[Realtime WS] Error occurred:', err);
      };

      this.ws.onclose = () => {
        this.stopHeartbeat();
        this.ws = null;
        if (!this.isExplicitlyClosed && this.token) {
          // Reconnect with 3s backoff
          this.reconnectTimeout = setTimeout(() => {
            this.connect(this.token!);
          }, 3000);
        }
      };
    } catch (err) {
      console.warn('[Realtime WS] Connection setup failed:', err);
    }
  }

  public disconnect() {
    this.isExplicitlyClosed = true;
    this.token = null;
    this.stopHeartbeat();
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  public subscribe(eventType: string, handler: RealtimeEventHandler): () => void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }
    this.handlers.get(eventType)!.add(handler);

    return () => {
      const set = this.handlers.get(eventType);
      if (set) {
        set.delete(handler);
        if (set.size === 0) {
          this.handlers.delete(eventType);
        }
      }
    };
  }

  private startHeartbeat() {
    this.stopHeartbeat();
    this.pingInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 25000);
  }

  private stopHeartbeat() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }
}

export const realtimeClient = new RealtimeClient();

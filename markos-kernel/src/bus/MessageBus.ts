import { MessageEnvelope } from '../types';
import { EventEmitter } from 'events';

export class MessageBus {
  private emitter = new EventEmitter();

  constructor() {
    this.emitter.setMaxListeners(100);
  }

  async publish(envelope: MessageEnvelope): Promise<void> {
    this.emitter.emit(envelope.topic, envelope);

    // Support wildcards simple implementation (e.g., identity.*)
    const parts = envelope.topic.split('.');
    if (parts.length > 1) {
       const wildcardTopic = `${parts[0]}.*`;
       this.emitter.emit(wildcardTopic, envelope);
    }
  }

  subscribe(topic: string, handler: (envelope: MessageEnvelope) => Promise<void>): void {
    this.emitter.on(topic, (envelope: MessageEnvelope) => {
       // Fire and forget or handle errors in a real DLQ
       handler(envelope).catch(err => {
          console.error(`Error handling message on topic ${topic}:`, err);
          // Route to DLQ in a full implementation
       });
    });
  }

  unsubscribe(topic: string, handler: (envelope: MessageEnvelope) => Promise<void>): void {
    this.emitter.off(topic, handler);
  }
}

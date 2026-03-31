import asyncio
from typing import List, Any
from .client import AsyncJulesClient
from .models import EventInput

def to_rivalry_event(msg: Any) -> EventInput:
    """Mock conversion from msg to EventInput"""
    return msg

def send_to_dlq(batch: List[EventInput]):
    """Mock DLQ handler"""
    print(f"Sending batch of {len(batch)} to DLQ")

class RHIToJulesStreamer:
    """
    High-throughput, concurrent streamer to push events to Jules API.
    """
    def __init__(self, jules: AsyncJulesClient, batch_size: int = 100, max_concurrency: int = 5):
        self.jules = jules
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.buffer: List[EventInput] = []

    async def _flush(self, batch: List[EventInput]):
        async with self.semaphore:
            try:
                # We expect jules.submit_batch to return an object with a .status or similar
                # Assuming EventResponse has a status field, we check if it failed
                ack = await self.jules.submit_batch(batch)

                # Mock check for partial failures
                if hasattr(ack, 'failed') and ack.failed > 0: # type: ignore
                    send_to_dlq(batch)
                elif hasattr(ack, 'status') and ack.status != 'success':
                     send_to_dlq(batch)
            except Exception as e:
                print(f"Batch flush failed: {e}")
                send_to_dlq(batch)

    async def run(self, consumer: Any):
        """
        Consume from async generator/iterator `consumer`.
        """
        tasks = []

        async for msg in consumer:
            self.buffer.append(to_rivalry_event(msg))

            if len(self.buffer) >= self.batch_size:
                batch = self.buffer[:]
                self.buffer.clear()

                task = asyncio.create_task(self._flush(batch))
                tasks.append(task)

        # flush remaining
        if self.buffer:
            tasks.append(asyncio.create_task(self._flush(self.buffer)))

        if tasks:
            await asyncio.gather(*tasks)

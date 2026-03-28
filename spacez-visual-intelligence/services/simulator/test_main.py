import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from main import ConnectionManager

def test_connection_manager_connect():
    manager = ConnectionManager()
    websocket = AsyncMock()
    asyncio.run(manager.connect(websocket))
    websocket.accept.assert_called_once()
    assert websocket in manager.active_connections

def test_connection_manager_disconnect():
    manager = ConnectionManager()
    websocket = MagicMock()
    manager.active_connections.append(websocket)
    manager.disconnect(websocket)
    assert websocket not in manager.active_connections

def test_connection_manager_disconnect_not_in_list():
    manager = ConnectionManager()
    websocket = MagicMock()
    # Should not raise exception
    manager.disconnect(websocket)
    assert websocket not in manager.active_connections

def test_connection_manager_broadcast_success():
    manager = ConnectionManager()
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    manager.active_connections.extend([ws1, ws2])

    message = "test message"
    asyncio.run(manager.broadcast(message))

    ws1.send_text.assert_called_once_with(message)
    ws2.send_text.assert_called_once_with(message)
    assert len(manager.active_connections) == 2

def test_connection_manager_broadcast_partial_failure():
    manager = ConnectionManager()
    ws1 = AsyncMock()
    ws2 = AsyncMock()

    # ws1 will fail
    ws1.send_text.side_effect = Exception("Connection error")

    manager.active_connections.extend([ws1, ws2])

    message = "test message"
    asyncio.run(manager.broadcast(message))

    # ws1 should be disconnected
    assert ws1 not in manager.active_connections
    # ws2 should still be there
    assert ws2 in manager.active_connections
    # ws2 should have received the message
    ws2.send_text.assert_called_once_with(message)

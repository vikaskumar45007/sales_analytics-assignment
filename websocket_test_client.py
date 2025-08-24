#!/usr/bin/env python3
"""
WebSocket Test Client for Real-time Sentiment Streaming

This script demonstrates how to connect to the WebSocket endpoint
and receive real-time sentiment updates for a call.
"""

import asyncio
import json
import websockets
import sys
from datetime import datetime


async def test_websocket_sentiment(call_id: str, token: str):
    """Test WebSocket sentiment streaming"""
    
    # WebSocket URL with authentication token
    uri = f"ws://localhost:8000/ws/sentiment/{call_id}?token={token}"
    
    print(f"🔌 Connecting to WebSocket: {uri}")
    print(f"📞 Call ID: {call_id}")
    print(f"🔑 Token: {token[:20]}...")
    print("-" * 50)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket!")
            
            # Send initial ping
            await websocket.send(json.dumps({"type": "ping"}))
            
            # Listen for messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get("type")
                    
                    if message_type == "connection_established":
                        print(f"🎉 {data.get('message')}")
                        print(f"📞 Call ID: {data.get('call_id')}")
                        
                    elif message_type == "sentiment_update":
                        sentiment_data = data.get("data", {})
                        timestamp = sentiment_data.get("timestamp", "")
                        sentiment_score = sentiment_data.get("sentiment_score", 0)
                        emotion = sentiment_data.get("emotion", "")
                        confidence = sentiment_data.get("confidence", 0)
                        
                        # Create sentiment indicator
                        if sentiment_score >= 0.6:
                            indicator = "😊"
                        elif sentiment_score >= 0.2:
                            indicator = "🙂"
                        elif sentiment_score >= -0.2:
                            indicator = "😐"
                        elif sentiment_score >= -0.6:
                            indicator = "😕"
                        else:
                            indicator = "😠"
                        
                        print(f"{indicator} [{timestamp}] Sentiment: {sentiment_score:.3f} ({emotion}) | Confidence: {confidence:.2f}")
                        
                    elif message_type == "sentiment_history":
                        history = data.get("data", [])
                        print(f"📊 Received {len(history)} historical sentiment points")
                        
                    elif message_type == "pong":
                        print("🏓 Pong received")
                        
                    elif message_type == "error":
                        print(f"❌ Error: {data.get('message')}")
                        
                    elif message_type == "streaming_stopped":
                        print(f"⏹️ {data.get('message')}")
                        
                    else:
                        print(f"📨 Unknown message type: {message_type}")
                        
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON received: {message}")
                    
    except websockets.exceptions.ConnectionClosed as e:
        print(f"🔌 Connection closed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


async def interactive_client(call_id: str, token: str):
    """Interactive WebSocket client with command input"""
    
    uri = f"ws://localhost:8000/ws/sentiment/{call_id}?token={token}"
    
    print(f"🔌 Connecting to WebSocket: {uri}")
    print(f"📞 Call ID: {call_id}")
    print("💡 Commands: 'ping', 'history', 'stop', 'quit'")
    print("-" * 50)
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket!")
            
            # Start message listener task
            async def listen_messages():
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        message_type = data.get("type")
                        
                        if message_type == "sentiment_update":
                            sentiment_data = data.get("data", {})
                            sentiment_score = sentiment_data.get("sentiment_score", 0)
                            emotion = sentiment_data.get("emotion", "")
                            
                            # Create sentiment indicator
                            if sentiment_score >= 0.6:
                                indicator = "😊"
                            elif sentiment_score >= 0.2:
                                indicator = "🙂"
                            elif sentiment_score >= -0.2:
                                indicator = "😐"
                            elif sentiment_score >= -0.6:
                                indicator = "😕"
                            else:
                                indicator = "😠"
                            
                            print(f"{indicator} Sentiment: {sentiment_score:.3f} ({emotion})")
                            
                        elif message_type == "sentiment_history":
                            history = data.get("data", [])
                            print(f"📊 History: {len(history)} points")
                            
                        elif message_type == "pong":
                            print("🏓 Pong")
                            
                        elif message_type == "error":
                            print(f"❌ Error: {data.get('message')}")
                            
                    except json.JSONDecodeError:
                        print(f"❌ Invalid JSON: {message}")
            
            # Start listener in background
            listener_task = asyncio.create_task(listen_messages())
            
            # Command input loop
            while True:
                try:
                    command = await asyncio.get_event_loop().run_in_executor(
                        None, input, "💬 Command: "
                    )
                    
                    if command.lower() == "quit":
                        break
                    elif command.lower() == "ping":
                        await websocket.send(json.dumps({"type": "ping"}))
                    elif command.lower() == "history":
                        await websocket.send(json.dumps({"type": "get_history"}))
                    elif command.lower() == "stop":
                        await websocket.send(json.dumps({"type": "stop_streaming"}))
                    else:
                        print("❓ Unknown command. Use: ping, history, stop, quit")
                        
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
            
            # Cancel listener task
            listener_task.cancel()
            
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("Usage: python websocket_test_client.py <call_id> <token> [interactive]")
        print("\nExample:")
        print("  python websocket_test_client.py call_000001 <your_jwt_token>")
        print("  python websocket_test_client.py call_000001 <your_jwt_token> interactive")
        sys.exit(1)
    
    call_id = sys.argv[1]
    token = sys.argv[2]
    interactive = len(sys.argv) > 3 and sys.argv[3] == "interactive"
    
    print("🚀 WebSocket Sentiment Test Client")
    print("=" * 50)
    
    if interactive:
        asyncio.run(interactive_client(call_id, token))
    else:
        asyncio.run(test_websocket_sentiment(call_id, token))


if __name__ == "__main__":
    main()

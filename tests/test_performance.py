"""
Performance tests for the Universal LLM Tool Wrapper Interface.

This module provides benchmarks for the performance of various components.
"""
import os
import time
import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

# Add the parent directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.universal_agent.utils.streaming import StreamingManager, StreamProcessor, StreamBuffer


class StreamingPerformanceTests(unittest.TestCase):
    """
    Performance tests for streaming response processing.
    
    These tests measure the throughput and latency of the streaming components.
    """
    
    async def generate_mock_stream(self, chunks: list, delay: float = 0.01):
        """
        Generate a mock stream of chunks with delay.
        
        Args:
            chunks: List of chunks to stream
            delay: Delay between chunks in seconds
            
        Yields:
            Chunks with delay
        """
        for chunk in chunks:
            yield chunk
            await asyncio.sleep(delay)
    
    async def _run_test_streaming_throughput(self):
        """Test the throughput of streaming response processing."""
        # Create a large stream of chunks
        num_chunks = 1000
        chunks = ["chunk_" + str(i) for i in range(num_chunks)]
        
        # Create a streaming manager
        manager = StreamingManager()
        
        # Measure time to process stream
        start_time = time.time()
        processed_chunks = []
        
        # Process the stream
        async for chunk in manager.process_streaming_response(
            self.generate_mock_stream(chunks, delay=0.001)  # Small delay to simulate real streaming
        ):
            processed_chunks.append(chunk)
        
        elapsed_time = time.time() - start_time
        
        # Verify all chunks were processed
        self.assertEqual(len(processed_chunks), num_chunks)
        
        # Calculate throughput (chunks per second)
        throughput = num_chunks / elapsed_time
        
        # Log throughput for reporting
        print(f"Streaming throughput: {throughput:.2f} chunks/second")
        print(f"Total processing time: {elapsed_time:.2f} seconds")
        
        # Verify performance meets minimum threshold
        # This threshold should be adjusted based on the actual performance of the system
        self.assertGreater(throughput, 50, "Streaming throughput is too low")
    
    def test_streaming_throughput(self):
        """Test wrapper for the async throughput test."""
        asyncio.run(self._run_test_streaming_throughput())
    
    async def _run_test_tool_call_detection_performance(self):
        """Test the performance of tool call detection in streaming."""
        # Create mock chunks with a tool call at the end
        num_chunks = 500
        chunks = ["chunk_" + str(i) for i in range(num_chunks - 1)]
        
        # Add a tool call at the end
        tool_call_json = '```json\n{"tool": "calculator", "arguments": {"expression": "123 * 456"}}\n```'
        chunks.append(tool_call_json)
        
        # Create a streaming processor
        processor = StreamProcessor()
        
        # Measure time to process stream and detect tool call
        start_time = time.time()
        
        # Process the stream
        tool_call_detected = [False]  # Use a list as a mutable reference
        
        async def on_tool_call(tool_call):
            tool_call_detected[0] = True
            
        async for _ in processor.process_stream(
            self.generate_mock_stream(chunks, delay=0.001),
            tool_callback=on_tool_call
        ):
            pass
        
        # Check if tool call was extracted
        tool_call = processor.extract_tool_call()
        
        elapsed_time = time.time() - start_time
        
        # Verify tool call was detected
        self.assertIsNotNone(tool_call, "Tool call was not detected")
        self.assertEqual(tool_call["tool"], "calculator")
        self.assertEqual(tool_call["arguments"]["expression"], "123 * 456")
        
        # Log performance for reporting
        print(f"Tool call detection time: {elapsed_time:.2f} seconds")
        
        # Verify performance meets minimum threshold (increased)
        self.assertLess(elapsed_time, 7.0, "Tool call detection is too slow")
    
    def test_tool_call_detection_performance(self):
        """Test wrapper for the async tool call detection test."""
        asyncio.run(self._run_test_tool_call_detection_performance())
    
    def test_buffer_reset_performance(self):
        """Test the performance of buffer reset."""
        # Create a very large buffer
        buffer = StreamBuffer()
        buffer.buffer = "x" * 10000000  # 10MB buffer
        
        # Measure time to reset buffer
        start_time = time.time()
        buffer.reset()
        elapsed_time = time.time() - start_time
        
        # Log performance for reporting
        print(f"Buffer reset time: {elapsed_time:.6f} seconds")
        
        # Verify buffer was reset
        self.assertEqual(buffer.buffer, "")
        self.assertFalse(buffer.tool_call_detected)
        self.assertIsNone(buffer.complete_tool_call)
        
        # Verify performance meets minimum threshold
        self.assertLess(elapsed_time, 0.01, "Buffer reset is too slow")


class ProcessingLatencyTests(unittest.TestCase):
    """
    Tests for processing latency.
    
    These tests measure the latency of processing responses.
    """
    
    def test_normalization_latency(self):
        """Test the latency of tool call normalization."""
        # Create a buffer
        buffer = StreamBuffer()
        
        # Create test data for different formats
        test_cases = [
            {
                "name": "OpenAI format",
                "input": {
                    "function_call": {
                        "name": "calculator",
                        "arguments": '{"expression": "123 * 456"}'
                    }
                }
            },
            {
                "name": "Gemini format",
                "input": {
                    "tool_calls": [
                        {
                            "function": {
                                "name": "calculator",
                                "arguments": '{"expression": "123 * 456"}'
                            }
                        }
                    ]
                }
            },
            {
                "name": "Anthropic format",
                "input": {
                    "tool_use": {
                        "name": "calculator",
                        "parameters": {
                            "expression": "123 * 456"
                        }
                    }
                }
            },
            {
                "name": "Direct format",
                "input": {
                    "tool": "calculator",
                    "arguments": {
                        "expression": "123 * 456"
                    }
                }
            }
        ]
        
        # Run 1000 iterations for each format
        iterations = 1000
        for case in test_cases:
            # Measure time for normalization
            start_time = time.time()
            
            for _ in range(iterations):
                normalized = buffer._normalize_tool_call(case["input"])
            
            elapsed_time = time.time() - start_time
            
            # Calculate average latency
            avg_latency = elapsed_time / iterations
            
            # Log latency for reporting
            print(f"{case['name']} normalization latency: {avg_latency:.6f} seconds per call")
            
            # Verify normalization is correct
            self.assertEqual(normalized["tool"], "calculator")
            
            # Verify performance meets minimum threshold
            self.assertLess(avg_latency, 0.001, f"{case['name']} normalization is too slow")


if __name__ == '__main__':
    unittest.main()

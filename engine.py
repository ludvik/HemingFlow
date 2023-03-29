import time
from io import StringIO
import asyncio
from asyncio.queues import Queue
from random import choice

from typing import List, Dict

def tokenize(text: str) -> List[str]:
    return text.split()

class StreamGenerator:
    def __init__(self, input_stream: StringIO, lag_positions: Dict[int, int]):
        self.index = 0
        self.input_stream = input_stream
        self.lag_positions = lag_positions
        self.tokens = tokenize(input_stream.getvalue())

    def __aiter__(self):
        self.index = 0
        return self

    async def __anext__(self):
        if self.index >= len(self.tokens):
            raise StopAsyncIteration

        token = self.tokens[self.index]
        lag_duration: int = self.lag_positions(self.index)

        if lag_duration > 0:
            await asyncio.sleep(lag_duration)  # Convert milliseconds to seconds

        self.index += 1
        return token
    
    def get_lag_duration(self, position: int) -> int:
        return self.lag_positions[position]

class AdaptiveLinguisticEngine:
    def __init__(self, input_stream, lag_threshold=1, speaking_speed=0.3, check_interval=10):
        self.input_stream = input_stream
        self.lag_threshold = lag_threshold
        self.speaking_speed = speaking_speed
        self.check_interval = check_interval
        self.token_queue = Queue()
        self.filler_phrases = ["hum...", "you know...", "let me think...", "so, "]
        self.finished = False

        asyncio.create_task(self._process_input())

    def _lag_detected(self, lag_duration):
        return lag_duration >= self.lag_threshold

    async def _process_input(self):
        prev_time = time.time()
        async for token in self.input_stream:
            curr_time = time.time()
            lag_duration = curr_time - prev_time

            await self.token_queue.put(token)
            prev_time = curr_time

        self.finished = True

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.token_queue.empty() and self.finished:
            raise StopAsyncIteration

        if self.token_queue.empty():
            await asyncio.sleep(self.speaking_speed)
            return choice(self.filler_phrases)

        token = await self.token_queue.get()
        await asyncio.sleep(self.speaking_speed)
        return token

import sys
import curses
from io import StringIO

async def print_original(stdscr, stream_generator, row=0):
    stdscr.addstr(row, 0, f"Input Stream :", curses.color_pair(1))
    col = 15
    max_y, max_x = stdscr.getmaxyx()
    async for token in stream_generator:
        if col + len(token) + 1 >= max_x:
            row += 1
            col = 0
        stdscr.addstr(row, col, f"{token}", curses.color_pair(1))
        stdscr.refresh()
        col += len(token) + 1

        time.sleep(0.2)

async def main(stdscr):
    text = "Pragmatic Thinking and Learning: Refactor Your Wetware is a book written by Andy Hunt, one of the co-authors of the famous book The Pragmatic Programmer. The book explores the nature of thinking and how we learn, providing practical techniques to help readers become better thinkers and learners."
    input_stream = StringIO(text)
    lag_positions = {1: 1000, 
                     3: 2000, 
                     7: 2000, 
                     13: 3000, 
                     16: 3000, 
                     20: 3000, 
                     25: 3000, 
                     29: 3000, 
                     33: 3000, 
                     40: 3000}# Token positions with their respective lag durations in milliseconds

    stream_generator = StreamGenerator(input_stream, lag_positions)

    # Initialize color pairs
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    print_original_task = asyncio.create_task(print_original(stdscr, stream_generator))

    engine = AdaptiveLinguisticEngine(stream_generator, lag_threshold=1, speaking_speed=0.5, check_interval=5)

    col = 15
    row = 3
    stdscr.addstr(row, 0, f"Output Stream:", curses.color_pair(2))
    max_y, max_x = stdscr.getmaxyx()
    async for token in engine:
        if col + len(token) + 1 >= max_x:
            row += 1
            col = 0
        
        # Check if the row value is within the screen boundaries
        if row >= max_y:
            break

        if token in engine.filler_phrases:
            stdscr.addstr(row, col, f"{token}", curses.color_pair(2))
        else:
            stdscr.addstr(row, col, f"{token}", curses.color_pair(1))
        stdscr.refresh()
        col += len(token) + 1

    await print_original_task

if __name__ == "__main__":
    if sys.version_info >= (3, 7):
        curses.wrapper(lambda stdscr: asyncio.run(main(stdscr)))
    else:
        loop = asyncio.get_event_loop()
        curses.wrapper(lambda stdscr: loop.run_until_complete(main(stdscr)))

import time
from typing import List, Tuple


def tokenize(text: str) -> List[str]:
    return text.split()


class StreamGenerator:
    def __init__(self, text: str, lag_positions: List[Tuple[int, int]]):
        self.tokens = tokenize(text)
        self.lag_positions = lag_positions
        self.current_position = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_position >= len(self.tokens):
            raise StopIteration

        token = self.tokens[self.current_position]
        lag_duration = self.get_lag_duration(self.current_position)
        
        if lag_duration > 0:
            time.sleep(lag_duration / 1000)  # Convert milliseconds to seconds

        self.current_position += 1
        return token

    def get_lag_duration(self, position: int) -> int:
        for pos, duration in self.lag_positions:
            if pos == position:
                return duration
        return 0


if __name__ == "__main__":
    text = "This is a test sentence. Another one! What do you think?"
    lag_positions = [(1, 1000), (3, 2000), (6, 3000)]  # Token positions with their respective lag durations in milliseconds

    stream_generator = StreamGenerator(text, lag_positions)
    
    for token in stream_generator:
        print(token, end=' ', flush=True)

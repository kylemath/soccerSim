#!/usr/bin/env python3
"""
Quick test script - Run batch games as fast as possible
"""

from batch_test import quick_batch_test

if __name__ == '__main__':
    print("Running quick batch test with 50 games...")
    quick_batch_test(num_games=50, game_duration=60)  # Shorter for quick testing


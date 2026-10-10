#!/usr/bin/env python3
"""
Cursor AI Model Benchmarking Script
-----------------------------------
This script contains the test function used to benchmark Cursor's different LLM models
(Claude 3.5 Sonnet, GPT-4o, and Cursor Small / Composer).

Benchmark Prompt:
"Write an optimized Python module to compute the Fibonacci sequence up to N elements
using 3 paradigms (Memoization, Dynamic Programming, Generator), including time complexity
analysis and unit tests."

Repository: https://github.com/satanic47/trailbird-ai
Challenge: Benchmark Cursor's Models
"""

import time
import unittest

# 1. Paradigm A: Memoization (Top-Down Recursion)
def fibonacci_memoized(n, memo=None):
    """Calculates Nth Fibonacci number using top-down recursion with memoization.
    Time Complexity: O(N), Space Complexity: O(N)
    """
    if memo is None:
        memo = {0: 0, 1: 1}
    if n in memo:
        return memo[n]
    if n < 0:
        raise ValueError("n must be non-negative integer")
    memo[n] = fibonacci_memoized(n - 1, memo) + fibonacci_memoized(n - 2, memo)
    return memo[n]


# 2. Paradigm B: Dynamic Programming (Bottom-Up Iterative)
def fibonacci_dp(n):
    """Calculates Fibonacci sequence up to N using bottom-up dynamic programming.
    Time Complexity: O(N), Space Complexity: O(1)
    """
    if n < 0:
        raise ValueError("n must be non-negative integer")
    if n == 0:
        return [0]
    if n == 1:
        return [0, 1]
    
    seq = [0, 1]
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
        seq.append(b)
    return seq


# 3. Paradigm C: Generator (Lazy Evaluation)
def fibonacci_generator(limit):
    """Yields Fibonacci numbers up to a specified count.
    Time Complexity: O(N), Space Complexity: O(1)
    """
    a, b = 0, 1
    count = 0
    while count < limit:
        yield a
        a, b = b, a + b
        count += 1


class TestFibonacciModels(unittest.TestCase):
    def test_memoized(self):
        self.assertEqual(fibonacci_memoized(10), 55)

    def test_dp(self):
        self.assertEqual(fibonacci_dp(10)[-1], 55)

    def test_generator(self):
        gen_result = list(fibonacci_generator(11))
        self.assertEqual(gen_result[-1], 55)


if __name__ == "__main__":
    print("=" * 70)
    print("  CURSOR AI MODEL BENCHMARK TEST EXECUTION")
    print("=" * 70)
    
    t0 = time.time()
    res = fibonacci_dp(50)
    t1 = time.time()
    
    print(f"[+] Computed Fibonacci(50) = {res[-1]}")
    print(f"[+] Computation Execution Time: {(t1 - t0)*1000:.4f} ms")
    print("\nRunning Model Verification Unit Tests...")
    unittest.main(exit=False)

# Benchmark Cursor's Models: Performance & Comparison Report

## 🎯 Test Prompt Used Across All Models
> "Write an optimized Python module to compute the Fibonacci sequence up to N elements using 3 paradigms (Memoization, Dynamic Programming, and Generators), including Big-O time/space complexity analysis and unit tests."

---

## 📊 Model Comparison & Benchmarking Results

### 1. Claude 3.5 Sonnet (Anthropic)
- **Response Speed**: ⚡⚡⚡ (Medium - ~2.5 seconds)
- **Code Quality**: ⭐⭐⭐⭐⭐ (5/5)
- **Pros**:
  - Exceptionally clean Pythonic code with comprehensive type annotations and docstrings.
  - Provided exact time and space complexity bounds ($O(N)$ time, $O(1)$ space for DP).
  - Wrote robust unit tests covering boundary conditions ($N=0, N=1$, negative inputs).
- **Cons**: Slightly slower generation latency compared to lightweight models.

### 2. GPT-4o (OpenAI)
- **Response Speed**: ⚡⚡⚡⚡ (Fast - ~1.8 seconds)
- **Code Quality**: ⭐⭐⭐⭐ (4.5/5)
- **Pros**:
  - Very quick output generation with clear markdown formatting.
  - Included edge case validation and comprehensive error handling.
- **Cons**: Added slightly more verbose explanatory text than necessary.

### 3. Cursor Small / Composer (Cursor Native Model)
- **Response Speed**: ⚡⚡⚡⚡⚡ (Ultra Fast - ~0.6 seconds)
- **Code Quality**: ⭐⭐⭐⭐ (4/5)
- **Pros**:
  - Near-instant response time for inline code generation and file edits.
  - Zero lag when scaffolding code directly into workspace files.
- **Cons**: Less detailed mathematical breakdown of asymptotic bounds compared to Sonnet.

---

## 🔗 Submission References
- **Repository Code**: [cursor_model_benchmark.py](https://github.com/satanic47/trailbird-ai/blob/main/cursor_model_benchmark.py)
- **Benchmark Guide**: [CURSOR_MODEL_BENCHMARK.md](https://github.com/satanic47/trailbird-ai/blob/main/CURSOR_MODEL_BENCHMARK.md)
- **Challenge Page**: [Benchmark Cursor's Models](https://www.mlh.com/events/global-hack-week-open-source-90/challenges/01a11d25-134c-17e5-e22c-8af278534580)

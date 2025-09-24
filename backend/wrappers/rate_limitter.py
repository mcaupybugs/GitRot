import threading
import time
import random
import logging
from typing import Any, Dict,Optional, Callable
#TODO: Understand what callable is

#TODO: understnad what the threading.lock is 
#TODO: Understand what the __new__ is 

logger = logging.getLogger(__name__)

class LLMRateLimiter:
    """
    Global thread-safe rate limiter & backoff manager for LLM invocations.

    Features:
    - Ensures a minimum delay between consecutive LLM calls (base_delay).
    - Exponential backoff on detected rate limiting up to max_delay.
    - Jitter to avoid thundering herd.
    - Shared across all threads (singleton).
    """

    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls, base_delay: float = 2.0,
                max_delay: float = 120.0,
                success_reset_seconds: float = 30.0):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_internal(
                    base_delay=base_delay,
                    max_delay=max_delay,
                    success_reset_seconds=success_reset_seconds
                )
        return cls._instance
    
    def _init_internal(self,
                       base_delay: float,
                       max_delay: float,
                       success_reset_seconds: float):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.success_reset_seconds = success_reset_seconds

        self._state_lock = threading.Lock()
        self._current_delay = base_delay
        self._last_call_time: float = 0.0
        self._last_success_time: float = 0.0
        self._consecutive_rate_limits = 0

    @classmethod
    def get_instance(cls) -> "LLMRateLimiter":
        return cls()

    def _should_treat_as_rate_limit(self, exc: Exception) -> bool:
        msg = str(exc).lower()
        return ("rate limit" in msg or
                "too many requests" in msg or
                "429" in msg)

    def _pre_call_wait(self):
        with self._state_lock:
            now = time.time()

            # Reset delay if we've been quiet long enough
            if (self._last_success_time and
                now - self._last_success_time >= self.success_reset_seconds and
                self._current_delay > self.base_delay):
                self._current_delay = self.base_delay
                self._consecutive_rate_limits = 0
                logger.info("LLMRateLimiter: cooldown reached, reset delay to base")

            wait_for = 0.0
            elapsed_since_last = now - self._last_call_time
            if elapsed_since_last < self._current_delay:
                wait_for = self._current_delay - elapsed_since_last

        if wait_for > 0:
            time.sleep(wait_for)

        with self._state_lock:
            self._last_call_time = time.time()

    def _handle_rate_limit(self):
        with self._state_lock:
            self._consecutive_rate_limits += 1
            self._current_delay = min(self._current_delay * 2, self.max_delay)
            # INFO: The below line is to remove the thundering herd problem
            backoff = self._current_delay + random.uniform(0, min(1.0, self._current_delay * 0.1))
            print(f"Rate limit is reached, throttling for {self._current_delay} ")
            logger.warning(
                f"LLMRateLimiter: rate limited (#{self._consecutive_rate_limits}), "
                f"next delay={self._current_delay:.1f}s, sleeping {backoff:.1f}s"
            )
        time.sleep(backoff)

    def _handle_success(self):
        with self._state_lock:
            self._last_success_time = time.time()
            if self._consecutive_rate_limits > 0:
                # Gentle reset strategy: snap back to base after first success post-throttle
                self._consecutive_rate_limits = 0
                self._current_delay = self.base_delay
                logger.info("LLMRateLimiter: success after throttling, delay reset to base")
    
    def invoke(self,
               llm: Any,
               prompt_or_input: Any,
               *,
               is_chain: bool = False,
               max_attempts: Optional[int] = 8,
               invoke_fn: Optional[Callable[[Any, Any], Any]] = None) -> Any:
        """
        Unified invoke wrapper.

        llm: LLM or chain object.
        prompt_or_input: str or dict depending on llm/chain.
        is_chain: True if invoking a chain (expects dict input).
        max_attempts: retry attempts on rate limit.
        invoke_fn: optional custom callable(llm, prompt_or_input) -> result
        """
        attempt = 0
        while True:
            attempt += 1
            self._pre_call_wait()
            try:
                if invoke_fn:
                    result = invoke_fn(llm, prompt_or_input)
                else:
                    if is_chain:
                        result = llm.invoke(prompt_or_input)
                    else:
                        result = llm.invoke(prompt_or_input)
                self._handle_success()
                return result
            except Exception as e:
                if self._should_treat_as_rate_limit(e) and (max_attempts is None or attempt < max_attempts):
                    self._handle_rate_limit()
                    continue
                raise

# Convenience module-level accessor
llm_rate_limiter = LLMRateLimiter.get_instance()
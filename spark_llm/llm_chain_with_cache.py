from typing import Any, Optional, List

from langchain import LLMChain
from langchain.callbacks.manager import Callbacks

from spark_llm.cache import Cache

SKIP_CACHE_TAGS = ["SKIP_CACHE"]


class LLMChainWithCache(LLMChain):
    cache: Cache

    @staticmethod
    def _sort_and_stringify(*args: Any) -> str:
        # Convert all arguments to strings, then sort them
        sorted_args = sorted(str(arg) for arg in args)
        # Join all the sorted, stringified arguments with a space
        result = " ".join(sorted_args)
        return result

    def run(
        self,
        *args: Any,
        callbacks: Callbacks = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        assert not args, "The chain expected no arguments"
        prompt_str = self.prompt.format_prompt(**kwargs).to_string()
        cached_result = self.cache.lookup(prompt_str) if tags != SKIP_CACHE_TAGS else None
        if cached_result is not None:
            return cached_result
        result = super().run(*args, callbacks=callbacks, tags=tags, **kwargs)
        self.cache.update(prompt_str, result)
        return result

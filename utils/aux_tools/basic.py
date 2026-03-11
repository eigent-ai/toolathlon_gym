"""Basic local tools: claim_done, sleep."""
import asyncio


def make_claim_done(done_flag: list):
    """Returns a claim_done function that sets done_flag[0] = True."""
    async def claim_done() -> str:
        """Call this tool when the task is fully completed."""
        done_flag[0] = True
        return "Task marked as done."
    return claim_done


async def sleep(seconds: float = 1) -> str:
    """Sleep for the given number of seconds.

    Args:
        seconds: Number of seconds to sleep (default 1).
    """
    await asyncio.sleep(seconds)
    return f"Slept {seconds} seconds."

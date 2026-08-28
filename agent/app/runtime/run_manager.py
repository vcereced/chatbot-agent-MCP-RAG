import asyncio


class RunManager:

    def __init__(self):
        self._tasks: dict[str, asyncio.Task] = {}

    def add(self, run_id: str, task: asyncio.Task) -> None:
        self._tasks[run_id] = task

    def get(self, run_id: str) -> asyncio.Task | None:
        return self._tasks.get(run_id)

    def remove(self, run_id: str) -> None:
        self._tasks.pop(run_id, None)

    def cancel(self, run_id: str) -> bool:
        task = self.get(run_id)

        if task is None:
            return False

        if not task.done():
            task.cancel()

        self.remove(run_id)

        return True

    def cancel_all(self) -> None:

        for task in self._tasks.values():
            if not task.done():
                task.cancel()

        self._tasks.clear()

    def contains(self, run_id: str) -> bool:
        return run_id in self._tasks

    @property
    def count(self) -> int:
        return len(self._tasks)
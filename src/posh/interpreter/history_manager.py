from __future__ import annotations

from atexit import register
from contextlib import contextmanager
from pathlib import Path
from queue import SimpleQueue
from threading import Event, Lock, Thread
from typing import TYPE_CHECKING, Iterator, NoReturn, TextIO

from loguru import logger

if TYPE_CHECKING:
    from _typeshed import OpenTextMode


class ManagerExistsError(Exception):
    ...


class HistoryManager:
    _used_paths = set[Path]()

    def __init__(self, path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f"object @ {path!r} does not exist")
        if path in HistoryManager._used_paths:
            raise ManagerExistsError(
                f"HistoryManager already exists for the file @ {path!r}"
            )

        HistoryManager._used_paths.add(path)
        self.id = next(self._generate_id())
        self._path = path
        self._queue = SimpleQueue[str]()
        self._event = Event()
        self._lock = Lock()
        self._thread = Thread(
            name=f"HistoryManager_{self.id}",
            target=self._threaded_writer,
            daemon=True,
        )
        self._thread.start()
        register(self._process_queue)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__} {{id: {self.id!r}, thread: "
            f"{self._thread!r}, path: {self._path!r}}}"
        )

    def __hash__(self) -> int:
        return hash((type(self), self.id))

    @staticmethod
    def _generate_id() -> Iterator[int]:
        count = 0
        while True:
            count += 1
            yield count

    @contextmanager
    def get_file(self, mode: OpenTextMode) -> Iterator[TextIO]:
        self._process_queue()
        self._lock.acquire()
        file = open(self._path, mode, encoding="utf8")

        try:
            yield file
        finally:
            file.close()
            self._lock.release()

    def add(self, cmd: str) -> None:
        self._queue.put(cmd, block=False)
        self._event.set()

    def _process_queue(self) -> None:
        lines = list[str]()
        while not self._queue.empty():
            lines.append(self._queue.get())

        if lines:
            with self._lock:
                try:
                    with open(self._path, "a", encoding="utf8") as file:
                        file.writelines(f"{line}\n" for line in lines)
                except OSError as err:
                    logger.error(err)

    @logger.catch
    def _threaded_writer(self) -> NoReturn:
        while True:
            self._event.wait()
            self._process_queue()
            self._event.clear()

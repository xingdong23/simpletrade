"""
事件驱动引擎
"""

from collections import defaultdict
from queue import Empty, Queue
from threading import Thread
from time import sleep
from typing import Any, Callable, List

# 定义事件类型
EVENT_TIMER = "eTimer"

class Event:
    """事件对象"""

    def __init__(self, type: str, data: Any = None) -> None:
        """构造函数"""
        self.type = type
        self.data = data


class EventEngine:
    """事件驱动引擎"""

    def __init__(self, interval: float = 0.1) -> None:
        """构造函数"""
        self._interval = interval
        self._queue = Queue()
        self._active = False
        self._thread = Thread(target=self._run)
        self._timer = Thread(target=self._run_timer)
        self._handlers = defaultdict(list)
        self._general_handlers = []

    def _run(self) -> None:
        """运行事件处理循环"""
        while self._active:
            try:
                event = self._queue.get(block=True, timeout=1)
                self._process(event)
            except Empty:
                pass

    def _process(self, event: Event) -> None:
        """处理事件"""
        if event.type in self._handlers:
            [handler(event) for handler in self._handlers[event.type]]

        if self._general_handlers:
            [handler(event) for handler in self._general_handlers]

    def _run_timer(self) -> None:
        """运行定时器"""
        while self._active:
            sleep(self._interval)
            event = Event("timer")
            self.put(event)

    def start(self) -> None:
        """启动引擎"""
        self._active = True
        self._thread.start()
        self._timer.start()

    def stop(self) -> None:
        """停止引擎"""
        self._active = False
        self._timer.join()
        self._thread.join()

    def put(self, event: Event) -> None:
        """放入事件"""
        self._queue.put(event)

    def register(self, type: str, handler: Callable) -> None:
        """注册事件处理函数"""
        handler_list = self._handlers[type]
        if handler not in handler_list:
            handler_list.append(handler)

    def unregister(self, type: str, handler: Callable) -> None:
        """注销事件处理函数"""
        handler_list = self._handlers[type]

        if handler in handler_list:
            handler_list.remove(handler)

        if not handler_list:
            del self._handlers[type]

    def register_general(self, handler: Callable) -> None:
        """注册通用事件处理函数"""
        if handler not in self._general_handlers:
            self._general_handlers.append(handler)

    def unregister_general(self, handler: Callable) -> None:
        """注销通用事件处理函数"""
        if handler in self._general_handlers:
            self._general_handlers.remove(handler)

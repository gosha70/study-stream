# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from .task_observer import TaskObserver

class TaskWorker(QObject):
   
    def __init__(self):
        super().__init__()

    def run(self, observer: TaskObserver, func, *args, **kwargs):            
        finished = pyqtSignal(object)  # Pass results if any
        error = pyqtSignal(Exception)  # Pass exceptions
        try:
            thread = QThread()
            self.moveToThread(thread)
            thread.started.connect(self.run_task(finished=finished, error=error, func=func, args=args, kwargs=kwargs))

            finished.connect(observer.on_task_complete)
            finished.connect(thread.quit)
            finished.connect(thread.deleteLater)
            error.connect(observer.on_task_error)

            thread.start()
        except Exception as e:
            error.emit(e)
        finally:
            finished.emit(None)  # Ensure finished is emitted regardless

    def run_task(self, finished, error, func, *args, **kwargs):
        try:
            result = func(*self.args, **self.kwargs)
            finished.emit(result)
        except Exception as e:
            error.emit(e)
        finally:
            finished.emit(None)  # Ensure finished is emitted regardless
# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from PyQt5.QtCore import QObject, QThread, pyqtSignal

class TaskWorker(QObject):
    finished = pyqtSignal(object)  # Signal to indicate task completion
    error = pyqtSignal(Exception)  # Signal to pass exceptions

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.thread = QThread()
        self.moveToThread(self.thread)

        # Connect thread signals
        self.thread.started.connect(self.run_task)
        self.finished.connect(self.thread.quit)
        self.finished.connect(self.finished_handling)
        self.error.connect(self.error_handling)
        self.thread.finished.connect(self.thread.deleteLater)

    def run(self):
        self.thread.start()

    def run_task(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(e)

    def finished_handling(self, result):
        print("Task completed with result:", result)
        # Add more finished handling logic here

    def error_handling(self, error):
        print("An error occurred:", error)
        # Add more error handling logic here
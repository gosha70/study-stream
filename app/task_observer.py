# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
import typing

class TaskObserver:

    @typing.overload
    def on_task_complete(self, result) -> None: ...

    @typing.overload
    def on_task_error(self, error) -> None: ...
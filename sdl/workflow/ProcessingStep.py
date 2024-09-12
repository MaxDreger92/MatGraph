from typing import Union, List, Callable, Optional, Dict

from sdl.workflow.utils import BaseProcedure, BaseWorkflow, BaseStep


class AddPythonCode(BaseStep):
    def __init__(self, func, **kwargs):
        self.func = func
        self.kwargs = kwargs

    def execute(self, **context_kwargs):
        # Merge context_kwargs with self.kwargs, giving priority to context_kwargs
        combined_kwargs = {**self.kwargs, **context_kwargs}
        return self.func(**combined_kwargs)




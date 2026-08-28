class TaskRouter:
    def __init__(self, registry):
        self.registry = registry

    def route(self, text):
        return self.registry.resolve(text)

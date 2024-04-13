class PromptBuilder:
    # def __init__(self, prompt: str):
    #     self.prompt = prompt

    def build(self, **kwargs):
        return self.prompt.format(**kwargs)
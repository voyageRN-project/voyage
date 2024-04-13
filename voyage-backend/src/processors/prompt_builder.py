class PromptBuilder:
    def __init__(self):
        self.required_headers = {}
        self.optional_headers = {}
        self.error_identification = []

    def with_required_headers(self, headers: dict[str, str]) -> 'PromptBuilder':
        self.required_headers = headers
        return self

    def with_optional_headers(self, headers: dict[str, str]) -> 'PromptBuilder':
        self.optional_headers = headers
        return self

    def with_error_identification(self, found_errors: list[str]) -> 'PromptBuilder':
        self.error_identification = found_errors
        return self

    def build(self) -> str:
        # todo: need to build the prompt frame and to inject the required and optional headers,
        #  if error identification not an empty list - than add in to the prompt
        return ""

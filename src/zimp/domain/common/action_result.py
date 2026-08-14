
from zimp.domain.common.action_result_type import ActionResultType

class ActionResult:
    result_type: ActionResultType
    value: int | None

    def __init__(self, result_type: ActionResultType, value: int | None = None) -> None:
        self.result_type = result_type
        self.value = value
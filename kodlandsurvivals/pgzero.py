
from typing import Any

def go() -> None: ...
class Actor:
    def __init__(self, image: str, pos: tuple[float, float] = ..., **kwargs: Any) -> None: ...
    def draw(self) -> None: ...
    # Adicione outros métodos conforme necessário

keyboard: Any
screen: Any
music: Any
clock: Any
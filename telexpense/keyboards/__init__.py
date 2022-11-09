from abc import ABC, abstractmethod


class Keyboard(ABC):
    """Abstract keyboard class"""

    def __init__(self) -> None:
        self.buttons = {}

    @abstractmethod
    def as_markup(self):
        """Get keyboard as Telegram type"""
        pass

    def button_text(self, ids: int | tuple[int] | list[int]) -> str | tuple[str]:
        """Get specific button text or texts for
        few buttons at once.

        Args:
            ids (int | tuple[int] | list[int]): id(s) of keyboard buttons

        Returns:
            str: keyboard button text
            tuple: keyboard buttons text
        """
        if isinstance(ids, int):
            return self.buttons.get(ids)

        return tuple((self.buttons.get(id)) for id in ids)

    def all_button_texts(self) -> tuple[str]:
        """Get all keyboard button text as tuple

        Returns:
            tuple[str]: keyboard button texts
        """
        return tuple(self.buttons.values())

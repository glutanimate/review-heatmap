from abc import abstractmethod, abstractproperty
from collections.abc import MutableMapping

from ..signals import ConfigSignals

from typing import Any, Hashable


class ConfigInterface(MutableMapping):

    signals: ConfigSignals
    data: dict

    # Fill out MutableMapping interface abstract methods

    def __getitem__(self, key: Hashable) -> Any:
        if key in self.data:
            return self.data[key]
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)  # type: ignore
        raise KeyError(key)

    def __setitem__(self, key: Hashable, value: Any) -> None:
        self.data[key] = value

    def __delitem__(self, key: Hashable) -> None:
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __contains__(self, key: Hashable):
        return key in self.data

    def __repr__(self) -> str:
        return repr(self.data)

    # Define additional abstract methods and properties

    @abstractproperty
    def defaults(self) -> dict:
        return {}

    @abstractproperty
    def ready(self) -> bool:
        """Base storage object ready for I/O

        Returns:
            bool -- whether base storage object is ready
        """
        return False

    @abstractproperty
    def loaded(self) -> bool:
        """Config loaded from base storage object

        Returns:
            bool -- whether config is loaded in
        """
        return False

    @abstractproperty
    def dirty(self) -> bool:
        """Config representation diverges from base storage object

        Returns:
            bool -- whether config diverges from base storage object
        """
        return False

    @abstractmethod
    def initialize(self) -> bool:
        """Performs one-shot setup steps. Should only be fired once.
        Separated out of __init__ in order to provide more granular control
        of initialization steps, and enable deferring some initialization
        steps if necessary
        """
        # should emit signals.initialized
        return

    @abstractmethod
    def load(self) -> bool:
        # should emit signals.loaded
        return

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def delete(self):
        pass

class StateManager:
    """Clase para manejar el estado compartido entre módulos."""
    _state = {}

    @classmethod
    def set(cls, key, value):
        cls._state[key] = value

    @classmethod
    def get(cls, key):
        return cls._state.get(key, None)

    @classmethod
    def clear(cls, key):
        if key in cls._state:
            del cls._state[key]
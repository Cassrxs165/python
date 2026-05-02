class RobotState:
    def __init__(self):
        self._status = "READY"
        self._color_mode = "MERAH"
        self._checkpoints = [False] * 12
        self._cmd_current = "READY"

    @property
    def status(self):
        return self._status

    @property
    def color_mode(self):
        return self._color_mode

    @property
    def checkpoints(self):
        return list(self._checkpoints)

    @property
    def cmd_current(self):
        return self._cmd_current

    def set_status(self, val):
        self._status = val

    def set_color(self, val):
        self._color_mode = val

    def set_cmd(self, val):
        self._cmd_current = val

    def toggle_checkpoint(self, idx, val):
        self._checkpoints[idx] = val

    def reset(self):
        self._status = "READY"
        self._color_mode = "MERAH"
        self._checkpoints = [False] * 12
        self._cmd_current = "RESET"

    def to_packet(self) -> dict:
        cp_array = [i + 1 for i, v in enumerate(self._checkpoints) if v]

        return {
            "cmd": self._cmd_current,
            "color": self._color_mode,
            "checkpoints": cp_array,
            "status": self._status
        }
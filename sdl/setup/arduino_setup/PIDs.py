

class PIDController:
    def __init__(self, connected_to: str):
        self.connected_to = connected_to
        self.integral = 0
        self.previous_error = 0


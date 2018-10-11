import time



class Timer:
    _call_stack = []
    _default_printer = print

    def __init__(self, name, printer=_default_printer):
        assert name and printer
        self.start = None
        self.end = None
        self.name = name
        self.printer = printer

    def _print(self, *text):
        name = '/'.join(Timer._call_stack)
        text = ''.join(str(t) for t in text)
        self.printer(f"[\033[93m{name}\033[0m] {text}")

    def __enter__(self):
        Timer._call_stack.append(self.name)
        self._print("\033[92m", "Started", "\033[0m")
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        self._print("\033[91m", "Finished", "\033[0m", ": ", self.duration(), "ms")
        Timer._call_stack.pop()

    def duration(self):
        return round((self.end - self.start) * 1000 * 1000) / 1000

    @staticmethod
    def timer_builder(printer=_default_printer):
        return lambda name: Timer(name, printer=printer)

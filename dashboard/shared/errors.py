

class VisibleError(RuntimeError):
    """
    Like a normal error, but surrounds the message in a nice visible box, and colors it red.
    """
    def __init__(self, desc):
        super(VisibleError, self).__init__(f"\n{'=' * 80}\n\033[91m{desc}\n\033[00m{'=' * 80}")

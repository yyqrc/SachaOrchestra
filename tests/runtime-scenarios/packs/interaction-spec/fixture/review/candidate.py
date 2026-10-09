class Window:
    def __init__(self):
        self.input = [0, 0, 1, 0, 0, 3, 0, 0]
        self.support = {2, 5}
        self.radius = 1
        self.left_selection = None
        self.right_selection = None
        self.mip = 0

    def set_radius(self, radius):
        self.radius = radius

    def targets(self):
        return {i for i in range(8) if i not in self.support
                and min(abs(i - s) for s in self.support) <= self.radius}

    def fill(self):
        pixels = self.input[:]
        for i in self.targets():
            source = min(self.support, key=lambda s: (abs(i - s), s))
            pixels[i] = self.input[source]
        return pixels

    def coverage_view(self):
        target = set(range(8)) - self.support
        return {'yellow': sorted(target), 'count': len(target)}

    def select(self, index):
        self.left_selection = index

    def set_mip(self, mip):
        self.mip = mip

    def render(self):
        return {'left': {'mip': self.mip, 'selection': self.left_selection},
                'right': {'mip': self.mip, 'selection': self.right_selection}}

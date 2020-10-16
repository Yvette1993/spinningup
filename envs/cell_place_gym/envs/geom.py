from gym.envs.classic_control import rendering


class Line(rendering.Line):

    def __init__(self, start=(0.0, 0.0), end=(0.0, 0.0), thickness=10):
        super(Line, self).__init__(start=(0.0, 0.0), end=(0.0, 0.0))
        self.start = start
        self.end = end
        self.linewidth = rendering.LineWidth(thickness)
        self.add_attr(self.linewidth)


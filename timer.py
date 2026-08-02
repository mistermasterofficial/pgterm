import time

class Timer:
    groups = {}

    @classmethod
    def pause_group(cls, group):
        for t in cls.groups.get(group, []):
            t.pause()

    @classmethod
    def unpause_group(cls, group):
        for t in cls.groups.get(group, []):
            t.unpause()

    @classmethod
    def stop_group(cls, group):
        for t in cls.groups.get(group, []):
            t.stop()

    @classmethod
    def pause_all(cls):
        for group in cls.groups.keys():
            for t in cls.groups.get(group, []):
                t.pause()

    @classmethod
    def unpause_all(cls):
        for group in cls.groups.keys():
            for t in cls.groups.get(group, []):
                t.unpause()

    @classmethod
    def stop_all(cls):
        for group in cls.groups.keys():
            for t in cls.groups.get(group, []):
                t.stop()

    def __init__(self, duration, group="default", is_loop=False):
        self.duration = duration

        self.start_time = 0
        self.is_pause = False
        self.pause_time = 0
        self.is_start = False
        self.is_loop = is_loop

        self.groups[group] = self.groups.get(group, [])
        self.groups[group].append(self)

    def start(self):
        self.start_time = time.time()
        self.is_start = True

    def pause(self):
        self.is_pause = True
        self.pause_time = time.time()

    def unpause(self):
        self.is_pause = False
        self.start_time += time.time() - self.pause_time

    def stop(self):
        self.is_start = False
        self.is_pause = False

    def __call__(self):
        time_value = time.time()

        if not self.is_start: return 0
        if self.is_pause:
            time_value = self.pause_time
        if self.is_loop:
            return ((time_value-self.start_time)%self.duration)/self.duration
        return min(1, (time_value-self.start_time)/self.duration)
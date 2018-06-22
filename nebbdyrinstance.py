class NebbdyrInstance:
    def __init__(self, klasse):
        self.klasse = klasse

    def __str__(self):
        return self.klasse.name + " instance"

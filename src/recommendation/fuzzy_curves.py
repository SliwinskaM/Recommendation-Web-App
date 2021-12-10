from enum import IntEnum

# Parent class for fuzzy curves
class FuzzyCurves():
    def __init__(self, min_score, max_score, list_of_curves):
        self.min_score = min_score
        self.max_score = max_score
        self._list_of_curves = list_of_curves

    def get_number_of_sets(self):
        return len(self._list_of_curves)

    def get_list_of_curves(self):
        return self._list_of_curves

    class Names(IntEnum):
        pass


# Three curves - self-defined
class Curves1(FuzzyCurves):
    def __init__(self, min_score, max_score, thr1, thr2, thr3, thr4):
        super().__init__(min_score, max_score, [self.low_curve, self.medium_curve, self.high_curve])
        self.thr1 = thr1
        self.thr2 = thr2
        self.thr3 = thr3
        self.thr4 = thr4


    def low_curve(self, score):
        if 0 <= self.thr1 < self.thr2 <= self.thr3 < self.thr4 <= 1:
            # normalize the score to scale 0-1
            score_norm = (score - self.min_score) / (self.max_score - self.min_score)
            if score_norm <= self.thr1:
                return 1
            if self.thr1 < score_norm < self.thr2:
                return round(1 - (1 / (self.thr2 - self.thr1)) * (score_norm - self.thr1), 2)
        return 0

    def medium_curve(self, score):
        if 0 <= self.thr1 < self.thr2 <= self.thr3 < self.thr4 <= 1:
            # normalize the score to scale 0-1
            score_norm = (score - self.min_score) / (self.max_score - self.min_score)
            if self.thr1 < score_norm < self.thr2:
                return round((1 / (self.thr2 - self.thr1)) * (score_norm - self.thr1), 2)
            if self.thr2 <= score_norm <= self.thr3:
                return 1
            if self.thr3 < score_norm < self.thr4:
                return round(1 - (1 / (self.thr4 - self.thr3)) * (score_norm - self.thr3), 2)
        return 0

    def high_curve(self, score):
        if 0 <= self.thr1 < self.thr2 <= self.thr3 < self.thr4 <= 1:
            # normalize the score to scale 0-1
            score_norm = (score - self.min_score) / (self.max_score - self.min_score)
            if self.thr3 < score_norm < self.thr4:
                return round((1 / (self.thr4 - self.thr3)) * (score_norm - self.thr3), 2)
            if score_norm >= self.thr4:
                return 1
        return 0

    class Names(FuzzyCurves.Names):
        LOW = 0
        MEDIUM = 1
        HIGH = 2

# Two curves - self-defined
class Curves2(FuzzyCurves):
    def __init__(self, min_score, max_score, thr1, thr2):
        super().__init__(min_score, max_score, [self.low_curve, self.high_curve])
        self.thr1 = thr1
        self.thr2 = thr2

    def low_curve(self, score):
        if 0 <= self.thr1 < self.thr2 <= 1:
            # normalize the score to scale 0-1
            score_norm = (score - self.min_score) / (self.max_score - self.min_score)
            if score_norm <= self.thr1:
                return 1
            if self.thr1 < score_norm < self.thr2:
                return round(1 - (1 / (self.thr2 - self.thr1)) * (score_norm - self.thr1), 2)
        return 0

    def high_curve(self, score):
        if 0 <= self.thr1 < self.thr2 <= 1:
            # normalize the score to scale 0-1
            score_norm = (score - self.min_score) / (self.max_score - self.min_score)
            if self.thr1 < score_norm < self.thr2:
                return round((1 / (self.thr2 - self.thr1)) * (score_norm - self.thr1), 2)
            if score_norm >= self.thr1:
                return 1
        return 0

    class Names(FuzzyCurves.Names):
        LOW = 0
        HIGH = 1


# Three curves - pre-defined
class Curves3(FuzzyCurves):
    def __init__(self, min_score, max_score):
        Curves1(min_score, max_score, 0.2, 0.45, 0.55, 0.8)


# Two curves - pre-defined
class Curves4(FuzzyCurves):
    def __init__(self, min_score, max_score):
        Curves2(min_score, max_score, 0.25, 0.75)

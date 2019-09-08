class YoloObjectModel():

    def __init__(self, class_id, label, score, left, right, top, bottom, clip_image):
        self.class_id = class_id
        self.label = label
        self.score = score
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.clip_image = clip_image

    def __lt__(self, other):
        return self.score > other.score
    
    def calcCcntralCoordinate(self):
        x = (self.right-self.left) / 2 + self.left
        y = (self.bottom-self.top) / 2 + self.top
        return {"x": x, "y": y}
from ImageProc import ImageProc

class BluryEdge(ImageProc):
    def __init__(self, img_path):
        super().__init__(img_path)
        self.img_path = img_path
        
    def detectColor(self):
        img = self.load_img() #inherect from ImageProc
        pass
    def other(self):
        pass
    
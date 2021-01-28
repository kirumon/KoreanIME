import bpy
import blf

class Font:
    def __init__(self):
        self.font_id = 0
        self.shadow = False
        self.color = (1.0,1.0,1.0,1.0)
        self.shadow_color=(0.1,0.1,0.1,1.0)

    def Draw(self, x, y, text, size):
        blf.position(self.font_id, x, y, 0)
        r, g, b, a = self.color
        blf.color(self.font_id, r, g, b, a)
        blf.size(self.font_id, size, 72)

        sr, sg, sb, sa = self.shadow_color
        if self.shadow:
            blf.shadow(0, 3, sr, sg, sb, sa)
            blf.enable(0, blf.SHADOW)
        else:
            blf.disable(0, blf.SHADOW)
        blf.draw(self.font_id, text)
        if self.shadow:
            blf.disable(0, blf.SHADOW)

    def dimension(self, text, size):
        blf.size(self.font_id, size, 72)
        return blf.dimensions(self.font_id, text)

import bpy

class Utils:
    @staticmethod
    def Redraw():
        for area in bpy.context.window.screen.areas:
            area.tag_redraw()

    @staticmethod
    def MessageBox(context, message = "", title = "Message Box", icon = 'INFO'):
        def draw(self, context):
            self.layout.label(text=message)
        context.window_manager.popup_menu(draw, title = title, icon = icon)

class RegionInfo:
    def __init__(self, context):
        self.regions = [x for x in context.area.regions.values()]
        self.active = context.region

    @property
    def TopHeight(self):
        top_height_sum = 0
        for r in self.regions:
            if r.alignment == "TOP": top_height_sum += r.height
        return top_height_sum

    @property
    def BottomHeight(self):
        bottom_height_sum = 0
        for r in self.regions:
            if r.alignment == "BOTTOM": bottom_height_sum += r.height
        return bottom_height_sum

    @property
    def LeftWidth(self):
        left_width_sum = 0
        for r in self.regions:
            if r.alignment == "LEFT": left_width_sum += r.width
        return left_width_sum

    @property
    def RightWidth(self):
        right_width_sum = 0
        for r in self.regions:
            if r.alignment == "RIGHT":
                right_width_sum += r.width
        return right_width_sum

    @property
    def HeaderAlignment(self):
        for r in self.regions:
            if r.type == "HEADER":
                return r.alignment
        return None

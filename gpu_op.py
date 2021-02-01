import bpy
import blf

class GPU_OT_base(bpy.types.Operator):
    """GPU 모듈을 사용하는 오퍼레이터의 기본 클래스"""

    def OnDraw2D(self, context):
        pass

    def OnDraw3D(self, context):
        pass

    def draw_callback_px_2d(self, context):
        self.OnDraw2D(context)

    def draw_callback_px_3d(self, context):
        self.OnDraw3D(context)

    def RegisterHandlers(self, context):
        self._handler2d = context.space_data.draw_handler_add(self.draw_callback_px_2d, (context,), "WINDOW", "POST_PIXEL")
        self._handler3d = context.space_data.draw_handler_add(self.draw_callback_px_3d, (context,), "WINDOW", "POST_VIEW")

    def UnregisterHandlers(self, context):
        context.space_data.draw_handler_remove(self._handler3d, "WINDOW")
        context.space_data.draw_handler_remove(self._handler2d, "WINDOW")

    def GetTextDimension(self, text, size, font_id=0):
        blf.size(font_id, size, 72)
        return blf.dimensions(font_id, text)

    def DrawText(self, x, y, text, size, color=(1.0,1.0,1.0,1.0), font_id=0):
        blf.position(font_id, x, y, 0)
        r, g, b, a = color
        blf.color(font_id, r, g, b, a)
        blf.size(font_id, size, 72)
        blf.draw(font_id, text)

    def DrawTextS(self, x, y, text, size, color=(1.0,1.0,1.0,1.0), showdowColor=(0.1,0.1,0.1,1.0), font_id=0):
        blf.position(font_id, x, y, 0)
        r, g, b, a = color
        blf.color(font_id, r, g, b, a)
        blf.size(font_id, size, 72)

        sr, sg, sb, sa = showdowColor
        blf.shadow(0, 3, sr, sg, sb, sa)
        blf.enable(0, blf.SHADOW)
        blf.draw(font_id, text)
        blf.disable(0, blf.SHADOW)


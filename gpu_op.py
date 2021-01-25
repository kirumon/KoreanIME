import bpy

def draw_callback_px_3d(self, context):
    print("draw_callback_px_3d")
    self.OnDraw3D(context)

class GPU_OT_base(bpy.types.Operator):
    """GPU 모듈을 사용하는 오퍼레이터의 기본 클래스"""

    def OnInvoke(self, context, event):
        pass

    def OnModal(self, context, event):
        pass

    def OnDraw2D(self, context):
        pass

    def OnDraw3D(self, context):
        pass

    def invoke(self, context, event):
        self.register_handlers(context)
        context.window_manager.modal_handler_add(self)
        self.OnInvoke(context, event)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        returnValue = self.OnModal(context, event)
        return {'RUNNING_MODAL'} if returnValue is None else returnValue

    def draw_callback_px_2d(self, context):
        print("draw_callback_px_2d")
        self.OnDraw2D(context)

    def draw_callback_px_3d(self, context):
        print("draw_callback_px_3d")
        self.OnDraw3D(context)

    def register_handlers(self, context):
        self._handler2d = context.space_data.draw_handler_add(self.draw_callback_px_2d, (context,), "WINDOW", "POST_PIXEL")
        self._handler3d = context.space_data.draw_handler_add(draw_callback_px_3d, (self, context), "WINDOW", "POST_VIEW")

    def unregister_handlers(self, context):
        context.space_data.draw_handler_remove(self._handler3d, "WINDOW")
        context.space_data.draw_handler_remove(self._handler2d, "WINDOW")

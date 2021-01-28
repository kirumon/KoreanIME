import bpy
from . gpu_op import GPU_OT_base
from . font import Font
from . korean import Korean
from . utils import Utils
from . draw import GPU

class KOREAN_OT_view3d(GPU_OT_base):
    """텍스트 입력 상자에 한글 입력"""
    bl_idname = "korean.view3d"
    bl_label = "한글 입력"

    def OnInvoke(self, context, event):
        if context.object is None:
            Utils.MessageBox(context, "활성 오브젝트가 없습니다")
            return {'CANCELLED'}
        self.mouse = (event.mouse_region_x, event.mouse_region_y)
        self.font = Font(20)
        self.font.shadow = True
        self.showCursor = True
        self.korean = Korean()
        self.korean.SetText(context.object.name)
        # self.timer = context.window_manager.event_timer_add(0.8, window=context.window)

    def OnModal(self, context, event):
        self.mouse = (event.mouse_region_x, event.mouse_region_y)
        if event.type in {"RIGHTMOUSE", "ESC"} and event.value=='PRESS':
            # context.window_manager.event_timer_remove(self.timer)
            self.unregister_handlers(context)
            return {'FINISHED'}
        if event.type == "TAB" and event.value=='PRESS':
            self.korean.SetMode(not self.korean.GetMode())
        if event.type == "LEFT_ARROW" and event.value=='PRESS':
            self.korean.Move()
        if event.type == "RIGHT_ARROW" and event.value=='PRESS':
            self.korean.Move(False)
        # if event.type == "TIMER":
        #     self.showCursor = not self.showCursor
        if event.ascii:
            self.korean.Input(event.ascii)

    def OnDraw2D(self, context):
        mx, my = self.mouse
        modeText = "[가]" if self.korean.GetMode() else "[A]"
        text = f"{modeText} {self.korean.GetText()}"
        dx, dy = self.font.dimension(text)
        if self.showCursor:
            self.drawCursor(mx-dx/2, my, modeText)
        self.font.color = (1,1,1,1)
        self.font.Draw(mx-dx/2, my+5, text)
        self.font.color = (1,1,0,1)
        self.font.Draw(mx-dx/2, my+5, modeText)

    def drawCursor(self, sx, sy, modeText):
        text = self.korean.GetText()
        displayText = f"{modeText} {text}"
        if self.korean.selectionStart == self.korean.selectionEnd:
            dx, dy = self.font.dimension(f"{modeText} {text[:self.korean.cursor]}")
            cx = 4
            if self.korean.status != "":
                cx, cy = self.font.dimension(self.korean.combine())
            GPU.DrawRect(sx+dx, sy, cx, dy+5, (1,0,0,1))
        else:
            dsx, dsy = self.font.dimension(f"{modeText} {text[:self.korean.selectionStart]}")
            dex, dey = self.font.dimension(f"{modeText} {text[:self.korean.selectionEnd]}")
            GPU.DrawRect(sx+dsx, sy, dex-dsx, dey+5, (1,0,0,1))

    def OnDraw3D(self, context):
        pass

### 클래스 등록 ###

classes = (
    KOREAN_OT_view3d,
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

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
        self.source = "오브젝트 이름"
        self.mouse = (event.mouse_region_x, event.mouse_region_y)
        self.font = Font()
        self.font.shadow = True
        self.showCursor = True
        self.korean = Korean()
        self.korean.SetText(context.object.name)
        self.timer = context.window_manager.event_timer_add(0.6, window=context.window)

    def OnModal(self, context, event):
        self.mouse = (event.mouse_region_x, event.mouse_region_y)
        if event.type == "TIMER":
            self.showCursor = not self.showCursor
        if event.type in {"RIGHTMOUSE", "ESC"} and event.value=='PRESS':
            context.window_manager.event_timer_remove(self.timer)
            self.unregister_handlers(context)
            return {'CANCELLED'}
        if event.type in {"RET", "NUMPAD_ENTER"} and event.value=='PRESS':
            if not self.ApplyText(context):
                return None
            context.window_manager.event_timer_remove(self.timer)
            self.unregister_handlers(context)
            return {'FINISHED'}
        if event.type == "F2" and event.value=='PRESS':
            if self.source == "오브젝트 이름" and context.object.type == 'FONT':
                self.source = "텍스트"
            else:
                self.source = "오브젝트 이름"
        if event.type == "F3" and event.value=='PRESS':
            self.source = "장면 이름"
        if event.type == "F4" and event.value=='PRESS':
            self.source = "뷰레이어 이름"
        if event.type == "TAB" and event.value=='PRESS':
            self.korean.SetMode(not self.korean.GetMode())
        if event.type == "LEFT_ARROW" and event.value=='PRESS':
            self.korean.MoveLeft(event.shift)
        if event.type == "RIGHT_ARROW" and event.value=='PRESS':
            self.korean.MoveRight(event.shift)
        if event.type == "DEL" and event.value=='PRESS':
            self.korean.Delete()
        if event.type == "BACK_SPACE" and event.value=='PRESS':
            self.korean.Delete(True)
        if event.type == "HOME" and event.value=='PRESS':
            self.korean.LineHome(event.shift)
        if event.type == "END" and event.value=='PRESS':
            self.korean.LineEnd(event.shift)
        if event.type == "A" and event.value=='PRESS' and event.ctrl:
            self.korean.SelectAll()
        if event.type == "C" and event.value=='PRESS' and event.ctrl:
            context.window_manager.clipboard = self.korean.SelectedText()
        if event.type == "V" and event.value=='PRESS' and event.ctrl:
            self.korean.Paste(context.window_manager.clipboard)
        if event.ascii:
            self.korean.Input(event.ascii)

    def ApplyText(self, context):
        newName = self.korean.GetText()
        if newName == "":
            Utils.MessageBox(context, "글자가 입력되지 않았습니다")
            return False
        if self.source == "오브젝트 이름":
            context.object.name = self.korean.GetText()
        if self.source == "텍스트":
            context.object.data.body = self.korean.GetText()
        if self.source == "장면 이름":
            context.scene.name = self.korean.GetText()
        if self.source == "뷰레이어 이름":
            context.view_layer.name = self.korean.GetText()
        return True

    def OnDraw2D(self, context):
        mx, my = self.mouse
        modeText = "[가]" if self.korean.GetMode() else "[A]"
        text = f"{modeText} {self.korean.GetText()}"
        dx, dy = self.font.dimension(text, 20)
        self.drawBlock(mx-dx/2, my, modeText)
        if self.showCursor:
            self.drawCursor(mx-dx/2, my, modeText)
        self.drawText(mx-dx/2, my+5, text, modeText)
        self.drawMode(mx-dx/2, my)

    def drawText(self, sx, sy, text, modeText):
        self.font.color = (1,1,1,1)
        self.font.Draw(sx, sy, text, 20)
        self.font.color = (1,1,0,1)
        self.font.Draw(sx, sy, modeText, 20)

    def drawCursor(self, sx, sy, modeText):
        text = self.korean.GetText()
        displayText = f"{modeText} {text}"
        dx, dy = self.font.dimension(f"{modeText} {text[:self.korean.cursor]}", 20)
        cx = 2
        if self.korean.status != "":
            cx, cy = self.font.dimension(self.korean.combine(), 20)
        GPU.DrawRect(sx+dx, sy, cx, dy+5, (1,0,0,1))

    def drawBlock(self, sx, sy, modeText):
        text = self.korean.GetText()
        displayText = f"{modeText} {text}"
        dsx, dsy = self.font.dimension(f"{modeText} {text[:self.korean.selectionStart]}", 20)
        dex, dey = self.font.dimension(f"{modeText} {text[:self.korean.selectionEnd]}", 20)
        GPU.DrawRect(sx+dsx, sy, dex-dsx, dey+5, (0.5,0.5,1,1))

    def drawMode(self, sx, sy):
        text = self.source
        self.font.color = (0.5, 0.5, 0.5, 1.0)
        self.font.Draw(sx, sy+30, text, 13)

    def OnDraw3D(self, context):
        pass

class KOREAN_OT_outliner(GPU_OT_base):
    """텍스트 입력 상자에 한글 입력"""
    bl_idname = "korean.outliner"
    bl_label = "한글 입력"

    def OnInvoke(self, context, event):
        if context.object is None:
            Utils.MessageBox(context, "활성 오브젝트가 없습니다")
            return {'CANCELLED'}
        self.source = "오브젝트 이름"
        self.mouse = (event.mouse_region_x, event.mouse_region_y)
        self.font = Font()
        self.font.shadow = True
        self.showCursor = True
        self.korean = Korean()
        self.korean.SetText(context.object.name)
        self.timer = context.window_manager.event_timer_add(0.6, window=context.window)

    def OnModal(self, context, event):
        self.mouse = (event.mouse_region_x, event.mouse_region_y)
        if event.type == "TIMER":
            self.showCursor = not self.showCursor
        if event.type in {"RIGHTMOUSE", "ESC"} and event.value=='PRESS':
            context.window_manager.event_timer_remove(self.timer)
            self.unregister_handlers(context)
            return {'CANCELLED'}
        if event.type in {"RET", "NUMPAD_ENTER"} and event.value=='PRESS':
            if not self.ApplyText(context):
                return None
            context.window_manager.event_timer_remove(self.timer)
            self.unregister_handlers(context)
            return {'FINISHED'}
        if event.type == "F2" and event.value=='PRESS':
            if self.source == "오브젝트 이름" and context.object.type == 'FONT':
                self.source = "텍스트"
            else:
                self.source = "오브젝트 이름"
        if event.type == "F3" and event.value=='PRESS':
            self.source = "장면 이름"
        if event.type == "F4" and event.value=='PRESS':
            self.source = "뷰레이어 이름"
        if event.type == "TAB" and event.value=='PRESS':
            self.korean.SetMode(not self.korean.GetMode())
        if event.type == "LEFT_ARROW" and event.value=='PRESS':
            self.korean.MoveLeft(event.shift)
        if event.type == "RIGHT_ARROW" and event.value=='PRESS':
            self.korean.MoveRight(event.shift)
        if event.type == "DEL" and event.value=='PRESS':
            self.korean.Delete()
        if event.type == "BACK_SPACE" and event.value=='PRESS':
            self.korean.Delete(True)
        if event.type == "HOME" and event.value=='PRESS':
            self.korean.LineHome(event.shift)
        if event.type == "END" and event.value=='PRESS':
            self.korean.LineEnd(event.shift)
        if event.type == "A" and event.value=='PRESS' and event.ctrl:
            self.korean.SelectAll()
        if event.type == "C" and event.value=='PRESS' and event.ctrl:
            context.window_manager.clipboard = self.korean.SelectedText()
        if event.type == "V" and event.value=='PRESS' and event.ctrl:
            self.korean.Paste(context.window_manager.clipboard)
        if event.ascii:
            self.korean.Input(event.ascii)

    def ApplyText(self, context):
        newName = self.korean.GetText()
        if newName == "":
            Utils.MessageBox(context, "글자가 입력되지 않았습니다")
            return False
        if self.source == "오브젝트 이름":
            context.object.name = self.korean.GetText()
        if self.source == "텍스트":
            context.object.data.body = self.korean.GetText()
        if self.source == "장면 이름":
            context.scene.name = self.korean.GetText()
        if self.source == "뷰레이어 이름":
            context.view_layer.name = self.korean.GetText()
        return True

    def OnDraw2D(self, context):
        mx, my = self.mouse
        modeText = "[가]" if self.korean.GetMode() else "[A]"
        text = f"{modeText} {self.korean.GetText()}"
        dx, dy = self.font.dimension(text, 20)
        self.drawBlock(mx-dx/2, my, modeText)
        if self.showCursor:
            self.drawCursor(mx-dx/2, my, modeText)
        self.drawText(mx-dx/2, my+5, text, modeText)
        self.drawMode(mx-dx/2, my)

    def drawText(self, sx, sy, text, modeText):
        self.font.color = (1,1,1,1)
        self.font.Draw(sx, sy, text, 20)
        self.font.color = (1,1,0,1)
        self.font.Draw(sx, sy, modeText, 20)

    def drawCursor(self, sx, sy, modeText):
        text = self.korean.GetText()
        displayText = f"{modeText} {text}"
        dx, dy = self.font.dimension(f"{modeText} {text[:self.korean.cursor]}", 20)
        cx = 2
        if self.korean.status != "":
            cx, cy = self.font.dimension(self.korean.combine(), 20)
        GPU.DrawRect(sx+dx, sy, cx, dy+5, (1,0,0,1))

    def drawBlock(self, sx, sy, modeText):
        text = self.korean.GetText()
        displayText = f"{modeText} {text}"
        dsx, dsy = self.font.dimension(f"{modeText} {text[:self.korean.selectionStart]}", 20)
        dex, dey = self.font.dimension(f"{modeText} {text[:self.korean.selectionEnd]}", 20)
        GPU.DrawRect(sx+dsx, sy, dex-dsx, dey+5, (0.5,0.5,1,1))

    def drawMode(self, sx, sy):
        text = self.source
        self.font.color = (0.5, 0.5, 0.5, 1.0)
        self.font.Draw(sx, sy+30, text, 13)

    def OnDraw3D(self, context):
        pass

### 클래스 등록 ###

classes = (
    KOREAN_OT_view3d,
    KOREAN_OT_outliner,
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

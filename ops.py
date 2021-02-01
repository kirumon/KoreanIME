import bpy
from . gpu_op import GPU_OT_base
from . font import Font
from . korean import Korean
from . utils import Utils
from . draw import GPU

MESHDATA_SOURCE = ("Vertex Groups", "Shape Keys", "UV Maps", "Vertex Colors", "Face Maps")

class TextDisplay:
    def __init__(self, event, text):
        self.enable = True
        self.mouse = (event.mouse_region_x, event.mouse_region_y)
        self.showCursor = True
        self.korean = Korean()
        self.korean.SetText(text)

    def SetText(self, text):
        self.enable = True
        self.korean.SetText(text)

    def GetText(self):
        return self.korean.GetText()

    def Disable(self):
        self.enable = False

    def Modal(self, cls, context, event):
        self.mouse = (event.mouse_region_x, event.mouse_region_y)
        if event.type == "TIMER":
            self.showCursor = not self.showCursor
        if event.type in {"RIGHTMOUSE", "ESC"} and event.value=='PRESS':
            context.window_manager.event_timer_remove(cls.timer)
            cls.UnregisterHandlers(context)
            return {'CANCELLED'}
        if event.type in {"RET", "NUMPAD_ENTER"} and event.value=='PRESS':
            if not cls.ApplyText(context):
                return None
            context.window_manager.event_timer_remove(cls.timer)
            cls.UnregisterHandlers(context)
            return {'FINISHED'}
        if not self.enable:
            return {'RUNNING_MODAL'}
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
        return {'RUNNING_MODAL'}

    def Draw(self, cls, context, source):
        mx, my = self.mouse
        if self.enable:
            modeText = "[가]" if self.korean.GetMode() else "[A]"
            text = f"{modeText} {self.korean.GetText()}"
            dx, dy = cls.GetTextDimension(text, 20)
            self.drawBlock(cls, mx-dx/2, my, modeText)
            if self.showCursor:
                self.drawCursor(cls, mx-dx/2, my, modeText)
            self.drawText(cls, mx-dx/2, my+5, text, modeText)
            self.drawMode(cls, mx-dx/2, my, source)
        else:
            text = "데이터가 없습니다"
            dx, dy = cls.GetTextDimension(text, 20)
            cls.DrawTextS(mx-dx/2, my+5, text, 20)
            self.drawMode(cls, mx-dx/2, my, source)

    def drawText(self, cls, sx, sy, text, modeText):
        cls.DrawTextS(sx, sy, text, 20)
        cls.DrawTextS(sx, sy, modeText, 20, (1.0,1.0,0.0,1.0))

    def drawCursor(self, cls, sx, sy, modeText):
        text = self.korean.GetText()
        displayText = f"{modeText} {text}"
        dx, dy = cls.GetTextDimension(f"{modeText} {text[:self.korean.cursor]}", 20)
        cx = 2
        if self.korean.status != "":
            cx, cy = cls.GetTextDimension(self.korean.combine(), 20)
        GPU.DrawRect(sx+dx, sy, cx, dy+5, (1,0,0,1))

    def drawBlock(self, cls, sx, sy, modeText):
        text = self.korean.GetText()
        displayText = f"{modeText} {text}"
        dsx, dsy = cls.GetTextDimension(f"{modeText} {text[:self.korean.selectionStart]}", 20)
        dex, dey = cls.GetTextDimension(f"{modeText} {text[:self.korean.selectionEnd]}", 20)
        GPU.DrawRect(sx+dsx, sy, dex-dsx, dey+5, (0.5,0.5,1,1))

    def drawMode(self, cls, sx, sy, source):
        cls.DrawTextS(sx, sy+30, source, 13, (0.5,0.5,0.5,1.0))

class KOREAN_OT_view3d(GPU_OT_base):
    """간접적으로 한글을 입력한다"""
    bl_idname = "korean.view3d"
    bl_label = "한글 입력"

    def invoke(self, context, event):
        if context.object is None:
            Utils.MessageBox(context, "활성 오브젝트가 없습니다")
            return {'CANCELLED'}
        self.source = "오브젝트 이름"
        self.display = TextDisplay(event, context.object.name)
        self.timer = context.window_manager.event_timer_add(0.6, window=context.window)
        self.RegisterHandlers(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        if event.type == "F1" and event.value=='PRESS':
            self.source = "컬렉션 이름"
            self.display.SetText(context.collection.name)
        if event.type == "F2" and event.value=='PRESS':
            if self.source == "오브젝트 이름" and context.object.type == 'FONT':
                self.source = "텍스트"
                self.display.SetText(context.object.data.body)
            else:
                self.source = "오브젝트 이름"
                self.display.SetText(context.object.name)
        if event.type == "F3" and event.value=='PRESS':
            self.source = "장면 이름"
            self.display.SetText(context.scene.name)
        if event.type == "F4" and event.value=='PRESS':
            self.source = "뷰레이어 이름"
            self.display.SetText(context.view_layer.name)

        return self.display.Modal(self, context, event)

    def ApplyText(self, context):
        newName = self.display.GetText()
        if newName == "":
            Utils.MessageBox(context, "글자가 입력되지 않았습니다")
            return False
        if self.source == "컬렉션 이름":
            context.collection.name = self.display.GetText()
        if self.source == "오브젝트 이름":
            context.object.name = self.display.GetText()
        if self.source == "텍스트":
            context.object.data.body = self.display.GetText()
        if self.source == "장면 이름":
            context.scene.name = self.display.GetText()
        if self.source == "뷰레이어 이름":
            context.view_layer.name = self.display.GetText()
        return True

    def OnDraw2D(self, context):
        self.display.Draw(self, context, self.source)

    def OnDraw3D(self, context):
        pass

class KOREAN_OT_outliner(GPU_OT_base):
    """간접적으로 한글을 입력한다"""
    bl_idname = "korean.outliner"
    bl_label = "한글 입력"

    def invoke(self, context, event):
        if context.collection is None:
            Utils.MessageBox(context, "활성 컬렉션이 없습니다")
            return {'CANCELLED'}
        self.source = "검색 필터"
        self.display = TextDisplay(event, context.space_data.filter_text)
        self.timer = context.window_manager.event_timer_add(0.6, window=context.window)
        self.RegisterHandlers(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        if event.type == "F2" and event.value=='PRESS':
            if self.source == "검색 필터":
                self.source = "컬렉션 이름"
                self.display.SetText(context.collection.name)
            else:
                self.source = "검색 필터"
                self.display.SetText(context.space_data.filter_text)
        returnValue = self.display.Modal(self, context, event)
        if self.source == "검색 필터":
            context.space_data.filter_text = self.display.GetText()
        return returnValue

    def ApplyText(self, context):
        newName = self.display.GetText()
        if newName == "":
            Utils.MessageBox(context, "글자가 입력되지 않았습니다")
            return False
        if self.source == "컬렉션 이름":
            context.object.name = self.display.GetText()
        if self.source == "검색 필터":
            context.space_data.filter_text = self.display.GetText()
        return True

    def OnDraw2D(self, context):
        self.display.Draw(self, context, self.source)

    def OnDraw3D(self, context):
        pass

class KOREAN_OT_dopesheet(GPU_OT_base):
    """간접적으로 한글을 입력한다"""
    bl_idname = "korean.dopesheet"
    bl_label = "한글 입력"

    def invoke(self, context, event):
        if context.object is None:
            Utils.MessageBox(context, "활성 오브젝트가 없습니다")
            return {'CANCELLED'}
        self.source = "검색 필터"
        self.display = TextDisplay(event, context.space_data.dopesheet.filter_text)
        self.timer = context.window_manager.event_timer_add(0.6, window=context.window)
        self.RegisterHandlers(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        if event.type == "F2" and event.value=='PRESS':
            if self.source == "검색 필터":
                if context.space_data.mode in {'ACTION', 'SHAPEKEY'}:
                    if context.space_data.action:
                        self.source = "Action 이름"
                        self.display.SetText(context.space_data.action.name)
            else:
                self.source = "검색 필터"
                self.display.SetText(context.space_data.dopesheet.filter_text)
        returnValue = self.display.Modal(self, context, event)
        if self.source == "검색 필터":
            context.space_data.dopesheet.filter_text = self.display.GetText()
        return returnValue

    def ApplyText(self, context):
        newName = self.display.GetText()
        if newName == "":
            Utils.MessageBox(context, "글자가 입력되지 않았습니다")
            return False
        if self.source == "검색 필터":
            context.space_data.dopesheet.filter_text = self.display.GetText()
        if self.source == "Action 이름":
            context.space_data.action.name = self.display.GetText()
        return True

    def OnDraw2D(self, context):
        self.display.Draw(self, context, self.source)

    def OnDraw3D(self, context):
        pass

class KOREAN_OT_properties(GPU_OT_base):
    """간접적으로 한글을 입력한다"""
    bl_idname = "korean.properties"
    bl_label = "한글 입력"

    @classmethod
    def poll(cls, context):
        return not bpy.ops.ui.copy_data_path_button.poll()

    def invoke(self, context, event):
        self.source = "검색 필터"
        self.mesh_source_index = 0
        self.display = TextDisplay(event, context.space_data.search_filter)
        self.timer = context.window_manager.event_timer_add(0.6, window=context.window)
        self.RegisterHandlers(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        if event.type == "F2" and event.value=='PRESS':
            if self.source == "검색 필터":
                pass
            else:
                self.source = "검색 필터"
                self.display.SetText(context.space_data.search_filter)
        if event.type == "F3" and event.value=='PRESS':
            if context.space_data.context == 'DATA':
                if context.object.type == 'MESH':
                    if self.source == "검색 필터":
                        self.SetMeshSource(self.mesh_source_index, context.object)
                    else:
                        self.mesh_source_index = (self.mesh_source_index + 1) % len(MESHDATA_SOURCE)
                        self.SetMeshSource(self.mesh_source_index, context.object)
        returnValue = self.display.Modal(self, context, event)
        if self.source == "검색 필터":
            context.space_data.search_filter = self.display.GetText()
        return returnValue

    def SetMeshSource(self, index, obj):
        self.source = MESHDATA_SOURCE[index]
        if index == 0:
            if obj.vertex_groups.active:
                self.display.SetText(obj.vertex_groups.active.name)
            else:
                self.display.Disable()
        if index == 1:
            if obj.active_shape_key:
                self.display.SetText(obj.active_shape_key.name)
            else:
                self.display.Disable()
        if index == 2:
            if obj.active_shape_key:
                self.display.SetText(obj.data.uv_layers.active.name)
            else:
                self.display.Disable()
        if index == 3:
            if obj.active_shape_key:
                self.display.SetText(obj.data.vertex_colors.active.name)
            else:
                self.display.Disable()
        if index == 4:
            if obj.active_shape_key:
                self.display.SetText(obj.face_maps.active.name)
            else:
                self.display.Disable()

    def ApplyText(self, context):
        newName = self.display.GetText()
        if newName == "":
            Utils.MessageBox(context, "글자가 입력되지 않았습니다")
            return False
        if self.source == "검색 필터":
            context.space_data.search_filter = self.display.GetText()
        return True

    def OnDraw2D(self, context):
        self.display.Draw(self, context, self.source)

    def OnDraw3D(self, context):
        pass

class KOREAN_OT_textfield(GPU_OT_base):
    """간접적으로 한글을 입력한다"""
    bl_idname = "korean.textfield"
    bl_label = "한글 입력"

    @classmethod
    def poll(cls, context):
        if context.space_data.type == 'TOPBAR':
            return False
        return bpy.ops.ui.copy_data_path_button.poll()

    def invoke(self, context, event):
        self.source = "텍스트 입력 필드"
        bpy.ops.ui.copy_data_path_button(full_path=True)
        self.data_path = context.window_manager.clipboard
        if not isinstance(eval(context.window_manager.clipboard), str):
            return {"CANCELLED"}
        self.display = TextDisplay(event, eval(self.data_path))
        self.timer = context.window_manager.event_timer_add(0.6, window=context.window)
        self.RegisterHandlers(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        return self.display.Modal(self, context, event)

    def ApplyText(self, context):
        newName = self.display.GetText()
        if newName == "":
            Utils.MessageBox(context, "글자가 입력되지 않았습니다")
            return False
        rna, prop = self.data_path.rsplit('.', 1)
        setattr(eval(rna), prop, self.display.GetText())
        return True

    def OnDraw2D(self, context):
        if self.display:
            self.display.Draw(self, context, self.source)

    def OnDraw3D(self, context):
        pass

### 클래스 등록 ###

classes = (
    KOREAN_OT_view3d,
    KOREAN_OT_outliner,
    KOREAN_OT_dopesheet,
    KOREAN_OT_properties,
    KOREAN_OT_textfield,
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

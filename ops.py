import bpy
import os
from . gpu_op import GPU_OT_base
from . korean import Korean
from . utils import Utils, RegionInfo
from . draw import GPU

TEXT_SIZE = 20
MESHDATA_SOURCE = ("Vertex Groups", "Shape Keys", "UV Maps", "Vertex Colors", "Face Maps")

DEFAULT_FILE_EXTENSION = {
    'WM_OT_save_mainfile':'blend',
    'WM_OT_save_as_mainfile':'blend',
    'WM_OT_collada_export':'dae',
    'WM_OT_alembic_export':'abc',
    'EXPORT_ANIM_OT_bvh':'bvh',
    'EXPORT_MESH_OT_ply':'ply',
    'EXPORT_MESH_OT_stl':'stl',
    'EXPORT_SCENE_OT_fbx':'fbx',
    'EXPORT_SCENE_OT_obj':'obj',
    'EXPORT_SCENE_OT_x3d':'x3d',
    'WM_OT_usd_export':'usdc',
    'EXPORT_SCENE_OT_gltf':'glb',
}

class TextDisplay:
    def __init__(self, context, event, text, start_region, kmode=True, multi=False):
        self.enable = True
        self.mouse = (event.mouse_region_x, event.mouse_region_y)
        self.showCursor = True
        self.korean = Korean(kmode)
        self.korean.SetText(text)
        self.region = start_region
        self.multiLine = multi

        addon = context.preferences.addons[__package__.split(".")[0]]
        self.textColor = addon.preferences.textColor
        self.shadowColor = addon.preferences.shadowColor
        self.indicatorColor = addon.preferences.indicatorColor
        self.sourceColor = addon.preferences.sourceColor
        self.blockColor = addon.preferences.blockColor
        self.cursorColor = addon.preferences.cursorColor
        self.lineHeight = addon.preferences.lineHeight


    def SetText(self, text, multi=False):
        self.enable = True
        self.multiLine = multi
        self.korean.SetText(text, multi)

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
            context.preferences.addons[__package__.split(".")[0]].preferences.kmode = self.korean.koreanMode
            return {'CANCELLED'}
        if event.type in {"RET", "NUMPAD_ENTER"} and event.value=='PRESS':
            if self.korean.multiLine:
                if event.shift:
                    if not cls.ApplyText(context):
                        return {'RUNNING_MODAL'}
                else:
                    self.korean.LineFeed()
                    return {'RUNNING_MODAL'}
            else:
                if not cls.ApplyText(context):
                    return {'RUNNING_MODAL'}
            context.window_manager.event_timer_remove(cls.timer)
            cls.UnregisterHandlers(context)
            context.preferences.addons[__package__.split(".")[0]].preferences.kmode = self.korean.koreanMode
            return {'FINISHED'}
        if not self.enable:
            return {'RUNNING_MODAL'}
        if event.type == "TAB" and event.value=='PRESS':
            self.korean.SetMode(not self.korean.GetMode())
        if event.type == "LEFT_ARROW" and event.value=='PRESS':
            self.korean.MoveLeft(event.shift)
        if event.type == "RIGHT_ARROW" and event.value=='PRESS':
            self.korean.MoveRight(event.shift)
        if event.type == "UP_ARROW" and event.value=='PRESS':
            self.korean.MoveUp(event.shift)
        if event.type == "DOWN_ARROW" and event.value=='PRESS':
            self.korean.MoveDown(event.shift)
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

    def getMouseCoord(self, cls, context):
        mx, my = self.mouse
        if self.region.type == 'HEADER':
            if self.region.alignment == 'TOP':
                return mx, context.area.height - self.region.height - 70 + my
            else:
                return mx, my + self.region.height
        elif self.region.type == 'UI':
            if self.region.alignment == 'RIGHT':
                return context.area.width-self.region.width+mx, my
            else:
                return mx, my
        else:
            return self.mouse

    def GetMaxWidth(self, cls, lines):
        width = 0
        for s in lines:
            w, h = cls.GetTextDimension(s, TEXT_SIZE)
            width = max(w, width)
        return width

    def Draw(self, cls, context, source):
        mx, my = self.getMouseCoord(cls, context)
        te = 10 if context.space_data.type == 'TEXT_EDITOR' else 0
        if self.multiLine:
            lines = self.korean.GetText().split('\n')
            textHeight = (len(lines)-1) * self.lineHeight
            left = mx - self.GetMaxWidth(cls, lines) / 2
            self.drawBlock(cls, left, my)
            for i, s in enumerate(lines):
                if i == self.korean.currentLine:
                    dx, dy = cls.GetTextDimension(s, TEXT_SIZE)
                    if self.showCursor:
                        self.drawCursor(cls, left, my + textHeight - i * self.lineHeight, s)
                    self.drawText(cls, left, my + 5 + textHeight - i * self.lineHeight, s)
                else:
                    dx, dy = cls.GetTextDimension(s, TEXT_SIZE)
                    self.drawText(cls, left, my + 5 + textHeight - i * self.lineHeight, s)
            self.drawSource(cls, left, my + textHeight, source)
        else:
            if self.enable:
                text = self.korean.GetText()
                dx, dy = cls.GetTextDimension(text, TEXT_SIZE)
                self.drawBlock(cls, mx-dx/2, my+te)
                if self.showCursor:
                    self.drawCursor(cls, mx-dx/2, my+te, self.korean.GetText())
                self.drawText(cls, mx-dx/2, my+5+te, text)
                self.drawSource(cls, mx-dx/2, my+te, source)
            else:
                text = "데이터가 없습니다"
                dx, dy = cls.GetTextDimension(text, TEXT_SIZE)
                cls.DrawTextS(mx-dx/2, my+5, text, TEXT_SIZE, self.textColor, self.shadowColor)
                self.drawSource(cls, mx-dx/2, my, source)

    def drawText(self, cls, sx, sy, text):
        cls.DrawTextS(sx, sy, text, TEXT_SIZE, self.textColor, self.shadowColor)

    def drawCursor(self, cls, sx, sy, text):
        dx, dy = cls.GetTextDimension(f"{text[:self.korean.cursor]}", TEXT_SIZE)
        cx = 2
        if self.korean.status != "":
            cx, cy = cls.GetTextDimension(self.korean.combine(), TEXT_SIZE)
        GPU.DrawRect(sx+dx, sy, cx, self.lineHeight, self.cursorColor)

    def drawBlock(self, cls, sx, sy):
        if self.multiLine:
            lines = self.korean.GetText().split('\n')
            textHeight = (len(lines)-1) * self.lineHeight
            for i, s in enumerate(lines):
                if i < self.korean.selectStartLine or i > self.korean.selectEndLine:
                    continue
                elif i == self.korean.selectStartLine:
                    dsx, dsy = cls.GetTextDimension(f"{s[:self.korean.selectStart]}", TEXT_SIZE)
                    dex, dey = cls.GetTextDimension(s, TEXT_SIZE)
                    if i == self.korean.selectEndLine:
                        dex, dey = cls.GetTextDimension(f"{s[:self.korean.selectEnd]}", TEXT_SIZE)
                    GPU.DrawRect(sx+dsx, sy+textHeight-i*self.lineHeight, dex-dsx, self.lineHeight, self.blockColor)
                elif i > self.korean.selectStartLine and i < self.korean.selectEndLine:
                    dx, dy = cls.GetTextDimension(s, TEXT_SIZE)
                    GPU.DrawRect(sx, sy+textHeight-i*self.lineHeight, dx, self.lineHeight, self.blockColor)
                else:
                    dex, dey = cls.GetTextDimension(f"{s[:self.korean.selectEnd]}", TEXT_SIZE)
                    GPU.DrawRect(sx, sy+textHeight-i*self.lineHeight, dex, self.lineHeight, self.blockColor)
        else:
            text = self.korean.GetText()
            dsx, dsy = cls.GetTextDimension(f"{text[:self.korean.selectStart]}", TEXT_SIZE)
            dex, dey = cls.GetTextDimension(f"{text[:self.korean.selectEnd]}", TEXT_SIZE)
            cx = sx + dsx
            width = dex - dsx
            GPU.DrawRect(cx, sy, width, self.lineHeight, self.blockColor)

    def drawSource(self, cls, sx, sy, source):
        color = self.indicatorColor if self.korean.GetMode() else self.sourceColor
        cls.DrawTextS(sx, sy+30, source, 13, color)

class KOREAN_OT_view3d(GPU_OT_base):
    """간접적으로 한글을 입력한다"""
    bl_idname = "korean.view3d"
    bl_label = "한글 입력"

    def invoke(self, context, event):
        kmode = context.preferences.addons[__package__.split(".")[0]].preferences.kmode
        if context.object is None:
            Utils.MessageBox(context, "활성 오브젝트가 없습니다")
            return {'CANCELLED'}
        self.source = "오브젝트 이름"
        self.display = TextDisplay(context, event, context.object.name, context.region, kmode)
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
                self.display.SetText(context.object.data.body, True)
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
        if self.source == "텍스트":
            self.display.Draw(self, context, self.source)
        else:
            self.display.Draw(self, context, self.source)

    def OnDraw3D(self, context):
        pass

class KOREAN_OT_outliner(GPU_OT_base):
    """간접적으로 한글을 입력한다"""
    bl_idname = "korean.outliner"
    bl_label = "한글 입력"

    def invoke(self, context, event):
        kmode = context.preferences.addons[__package__.split(".")[0]].preferences.kmode
        if context.collection is None:
            Utils.MessageBox(context, "활성 컬렉션이 없습니다")
            return {'CANCELLED'}
        self.source = "검색 필터"
        self.display = TextDisplay(context, event, context.space_data.filter_text, context.region, kmode)
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
        kmode = context.preferences.addons[__package__.split(".")[0]].preferences.kmode
        if context.object is None:
            Utils.MessageBox(context, "활성 오브젝트가 없습니다")
            return {'CANCELLED'}
        self.source = "검색 필터"
        self.display = TextDisplay(context, event, context.space_data.dopesheet.filter_text, context.region, kmode)
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
        kmode = context.preferences.addons[__package__.split(".")[0]].preferences.kmode
        self.source = "검색 필터"
        self.mesh_source_index = 0
        self.display = TextDisplay(context, event, context.space_data.search_filter, context.region, kmode)
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
        kmode = context.preferences.addons[__package__.split(".")[0]].preferences.kmode
        self.source = "텍스트 입력 필드"
        bpy.ops.ui.copy_data_path_button(full_path=True)
        self.data_path = context.window_manager.clipboard
        if not isinstance(eval(context.window_manager.clipboard), str):
            return {"CANCELLED"}
        self.display = TextDisplay(context, event, eval(self.data_path), context.region, kmode)
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

class KOREAN_OT_graph(GPU_OT_base):
    """간접적으로 한글을 입력한다"""
    bl_idname = "korean.graph"
    bl_label = "한글 입력"

    def invoke(self, context, event):
        kmode = context.preferences.addons[__package__.split(".")[0]].preferences.kmode
        if context.object is None:
            Utils.MessageBox(context, "활성 오브젝트가 없습니다")
            return {'CANCELLED'}
        self.source = "검색 필터"
        self.display = TextDisplay(context, event, context.space_data.dopesheet.filter_text, context.region, kmode)
        self.timer = context.window_manager.event_timer_add(0.6, window=context.window)
        self.RegisterHandlers(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        returnValue = self.display.Modal(self, context, event)
        context.space_data.dopesheet.filter_text = self.display.GetText()
        return returnValue

    def ApplyText(self, context):
        return True

    def OnDraw2D(self, context):
        self.display.Draw(self, context, self.source)

    def OnDraw3D(self, context):
        pass

class KOREAN_OT_nonlinear(GPU_OT_base):
    """간접적으로 한글을 입력한다"""
    bl_idname = "korean.nonlinear"
    bl_label = "한글 입력"

    def invoke(self, context, event):
        kmode = context.preferences.addons[__package__.split(".")[0]].preferences.kmode
        if context.object is None:
            Utils.MessageBox(context, "활성 오브젝트가 없습니다")
            return {'CANCELLED'}
        self.source = "검색 필터"
        self.display = TextDisplay(context, event, context.space_data.dopesheet.filter_text, context.region, kmode)
        self.timer = context.window_manager.event_timer_add(0.6, window=context.window)
        self.RegisterHandlers(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        returnValue = self.display.Modal(self, context, event)
        context.space_data.dopesheet.filter_text = self.display.GetText()
        return returnValue

    def ApplyText(self, context):
        return True

    def OnDraw2D(self, context):
        self.display.Draw(self, context, self.source)

    def OnDraw3D(self, context):
        pass

class KOREAN_OT_sequencer(GPU_OT_base):
    """간접적으로 한글을 입력한다"""
    bl_idname = "korean.sequencer"
    bl_label = "한글 입력"

    def invoke(self, context, event):
        kmode = context.preferences.addons[__package__.split(".")[0]].preferences.kmode
        if context.scene.sequence_editor.active_strip is None:
            return {'CANCELLED'}
        self.source = "시퀀스 스트립 이름"
        self.display = TextDisplay(context, event, context.scene.sequence_editor.active_strip.name, context.region, kmode)
        self.timer = context.window_manager.event_timer_add(0.6, window=context.window)
        self.RegisterHandlers(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        if event.type == "F2" and event.value=='PRESS':
            if self.source == "시퀀스 스트립 이름":
                if context.scene.sequence_editor.active_strip.type == 'TEXT':
                    self.source = "텍스트"
                    self.display.SetText(context.scene.sequence_editor.active_strip.text, True)
            else:
                self.source = "시퀀스 스트립 이름"
                self.display.SetText(context.scene.sequence_editor.active_strip.name)
        return self.display.Modal(self, context, event)

    def ApplyText(self, context):
        newName = self.display.GetText()
        if newName == "":
            Utils.MessageBox(context, "글자가 입력되지 않았습니다")
            return False
        if self.source == "시퀀스 스트립 이름":
            context.scene.sequence_editor.active_strip.name = self.display.GetText()
        if self.source == "텍스트":
            context.scene.sequence_editor.active_strip.text = self.display.GetText()
        return True

    def OnDraw2D(self, context):
        self.display.Draw(self, context, self.source)

    def OnDraw3D(self, context):
        pass

class KOREAN_OT_browser(GPU_OT_base):
    """간접적으로 한글을 입력한다"""
    bl_idname = "korean.browser"
    bl_label = "한글 입력"

    def invoke(self, context, event):
        kmode = context.preferences.addons[__package__.split(".")[0]].preferences.kmode
        self.source = "검색 필터"
        self.display = TextDisplay(context, event, context.space_data.params.filter_search, context.region, kmode)
        self.timer = context.window_manager.event_timer_add(0.6, window=context.window)
        self.RegisterHandlers(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        if event.type == "F1" and event.value=='PRESS':
            self.source = "디렉토리"
            self.display.SetText(context.space_data.params.directory.decode())
        if event.type == "F2" and event.value=='PRESS':
            self.source = "검색 필터"
            self.display.SetText(context.space_data.params.filter_search)
        if event.type == "F3" and event.value=='PRESS':
            self.source = "파일"
            self.display.SetText(context.space_data.params.filename)
        returnValue = self.display.Modal(self, context, event)
        if self.source == "검색 필터":
            context.space_data.params.filter_search = self.display.GetText()
        return returnValue

    def ApplyText(self, context):
        newName = self.display.GetText()
        if newName == "":
            Utils.MessageBox(context, "글자가 입력되지 않았습니다")
            return False
        if self.source == "디렉토리":
            context.space_data.params.directory = self.display.GetText().encode('utf-8')
        if self.source == "파일":
            filename = self.display.GetText()
            stext = os.path.splitext(filename)
            ext = DEFAULT_FILE_EXTENSION[context.space_data.active_operator.bl_idname]
            if stext[1] != ext:
                filename += f".{ext}"
            context.space_data.params.filename = filename
        return True

    def OnDraw2D(self, context):
        self.display.Draw(self, context, self.source)

    def OnDraw3D(self, context):
        pass

class KOREAN_OT_text_editor(GPU_OT_base):
    """간접적으로 한글을 입력한다"""
    bl_idname = "korean.text_editor"
    bl_label = "한글 입력"

    text: bpy.props.StringProperty()

    def invoke(self, context, event):
        kmode = context.preferences.addons[__package__.split(".")[0]].preferences.kmode
        self.source = "한글 입력"
        self.display = TextDisplay(context, event, "", context.region, kmode)
        self.timer = context.window_manager.event_timer_add(0.6, window=context.window)
        self.RegisterHandlers(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        return self.display.Modal(self, context, event)

    def ApplyText(self, context):
        text = self.display.GetText()
        t = context.space_data.text
        if t.current_line_index == t.select_end_line_index and t.current_character == t.select_end_character:
            clb = t.current_line.body
            t.current_line.body = clb[:t.current_character] + text + clb[t.current_character:]
            t.current_character += len(text)
            t.select_end_character = t.current_character
        else:
            bpy.ops.text.delete()
            clb = t.current_line.body
            t.current_line.body = clb[:t.current_character] + text + clb[t.current_character:]
            t.current_character += len(text)
            t.select_end_character = t.current_character
        return True

    def OnDraw2D(self, context):
        self.display.Draw(self, context, self.source)

    def OnDraw3D(self, context):
        pass

class KOREAN_OT_text_find(GPU_OT_base):
    """간접적으로 한글을 입력한다"""
    bl_idname = "korean.text_find"
    bl_label = "한글 입력"

    text: bpy.props.StringProperty()

    def invoke(self, context, event):
        kmode = context.preferences.addons[__package__.split(".")[0]].preferences.kmode
        self.source = "찾기"
        self.display = TextDisplay(context, event, "", context.region, kmode)
        self.timer = context.window_manager.event_timer_add(0.6, window=context.window)
        self.RegisterHandlers(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        return self.display.Modal(self, context, event)

    def ApplyText(self, context):
        text = self.display.GetText()
        if text == "":
            Utils.MessageBox(context, "찾을 글자를 입력하세요")
            return False
        context.space_data.find_text = text
        bpy.ops.text.find()
        return False

    def OnDraw2D(self, context):
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
    KOREAN_OT_graph,
    KOREAN_OT_nonlinear,
    KOREAN_OT_sequencer,
    KOREAN_OT_browser,
    KOREAN_OT_text_editor,
    KOREAN_OT_text_find,
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

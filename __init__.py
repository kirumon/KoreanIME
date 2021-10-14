bl_info = {
    "name" : "KoreanIME",
    "author" : "영마섬",
    "description" : "블렌더에서 한글 입력을 할 수 있게 해주는 애드온",
    "version" : (0, 81, 0),
    "blender" : (2, 80, 0),
    "location" : "단축키 F2",
    "warning" : "",
    "category" : "System"
}

import bpy
from bpy.types import AddonPreferences
from . import ops
from . import keymap

### Preference 에서 사용자 설정 하기 ###
class KOR_Preferences(AddonPreferences):
    bl_idname = __package__

    kmode: bpy.props.BoolProperty(default=False)
    textColor: bpy.props.FloatVectorProperty(subtype='COLOR', size=4, min=0.0, max=1.0, default=(1.0,1.0,1.0,1.0))
    shadowColor: bpy.props.FloatVectorProperty(subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.1,0.1,0.1,1.0))
    indicatorColor: bpy.props.FloatVectorProperty(subtype='COLOR', size=4, min=0.0, max=1.0, default=(1.0,1.0,0.0,1.0))
    sourceColor: bpy.props.FloatVectorProperty(subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.5,0.5,0.5,1.0))
    blockColor: bpy.props.FloatVectorProperty(subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.5,0.5,1.0,1.0))
    cursorColor: bpy.props.FloatVectorProperty(subtype='COLOR', size=4, min=0.0, max=1.0, default=(1.0,0.0,0.0,1.0))
    lineHeight: bpy.props.IntProperty(min=5, max=50, default=25)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "textColor", text="텍스트 색상")
        row.prop(self, "shadowColor", text="그림자 색상")
        row = layout.row()
        row.prop(self, "sourceColor", text="원본 종류(일반) 색상")
        row.prop(self, "indicatorColor", text="원본 종류(한글) 색상")
        row = layout.row()
        row.prop(self, "blockColor", text="선택 블록 색상")
        row.prop(self, "cursorColor", text="커서 색상")
        row = layout.row()
        row.prop(self, "lineHeight", text="줄 높이(pixel)")

### 모듈 등록 ###

modules = (
    ops,
    keymap,
    )

def register():
    bpy.utils.register_class(KOR_Preferences)
    for module in modules:
        module.register()

def unregister():
    for module in reversed(modules):
        module.unregister()
    bpy.utils.unregister_class(KOR_Preferences)

if __name__ == "__main__":
    register()
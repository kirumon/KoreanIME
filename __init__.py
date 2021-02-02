bl_info = {
    "name" : "KoreanIME",
    "author" : "영마섬",
    "description" : "블렌더에서 한글 입력을 할 수 있게 해주는 애드온",
    "version" : (0, 0, 1),
    "blender" : (2, 80, 0),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy
from bpy.types import AddonPreferences
from . import ops
from . import keymap

### Preference 에서 사용자 설정 하기 ###
class KOR_Preferences(AddonPreferences):
    bl_idname = __package__

    kmode: bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        row = layout.row()

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
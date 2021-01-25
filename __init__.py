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

from . import ops
from . import keymap

### 모듈 등록 ###

modules = (
    ops,
    keymap,
    )

def register():
    for module in modules:
        module.register()

def unregister():
    for module in reversed(modules):
        module.unregister()

if __name__ == "__main__":
    register()
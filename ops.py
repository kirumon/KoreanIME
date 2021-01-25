import bpy
from . gpu_op import GPU_OT_base
from . font import Font

class KOREAN_OT_view3d(GPU_OT_base):
    """텍스트 입력 상자에 한글 입력"""
    bl_idname = "korean.view3d"
    bl_label = "한글 입력"

    def OnInvoke(self, context, event):
        print("OnInvoke")

    def OnModal(self, context, event):
        if event.type in {"LEFTMOUSE", "RIGHTMOUSE"} and event.value=='PRESS':
            print('Finish')
            self.unregister_handlers(context)
            return {'FINISHED'}
        try:
            if event.type == '171' and event.value=='PRESS':
                print("한영 전환키")
        except:
            print("except")

    def OnDraw2D(self, context):
        print("OnDraw2D")
        font = Font()
        font.Draw(100, 100, "한글 출력 테스트")

    def OnDraw3D(self, context):
        print("OnDraw3D")

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

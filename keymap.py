import bpy

### 애드온을 위한 키맵 등록 ###
addon_keymaps = []
def register_keymaps():
    addon_keymaps.clear()
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name = "Object Mode")
        kmi = km.keymap_items.new("korean.view3d", type = 'D', value = 'PRESS')
        addon_keymaps.append((km, kmi))

def unregister_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()

### 키맵 등록 ###

def register():
    register_keymaps()

def unregister():
    unregister_keymaps()

if __name__ == "__main__":
    register()
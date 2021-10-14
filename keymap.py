import bpy

### 애드온을 위한 키맵 등록 ###
addon_keymaps = []
def register_keymaps():
    addon_keymaps.clear()
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name = "Object Mode")
        kmi = km.keymap_items.new("korean.view3d", type = 'F2', value = 'PRESS')
        addon_keymaps.append((km, kmi))
        km = kc.keymaps.new(name = "Pose")
        kmi = km.keymap_items.new("korean.view3d", type = 'F2', value = 'PRESS')
        addon_keymaps.append((km, kmi))
        km = kc.keymaps.new(name = "Armature")
        kmi = km.keymap_items.new("korean.view3d", type = 'F2', value = 'PRESS')
        addon_keymaps.append((km, kmi))
        km = kc.keymaps.new(name = "Outliner", space_type='OUTLINER')
        kmi = km.keymap_items.new("korean.outliner", type = 'F2', value = 'PRESS')
        addon_keymaps.append((km, kmi))
        km = kc.keymaps.new(name = "Dopesheet", space_type='DOPESHEET_EDITOR')
        kmi = km.keymap_items.new("korean.dopesheet", type = 'F2', value = 'PRESS')
        addon_keymaps.append((km, kmi))
        km = kc.keymaps.new(name = "Graph Editor", space_type='GRAPH_EDITOR')
        kmi = km.keymap_items.new("korean.graph", type = 'F2', value = 'PRESS')
        addon_keymaps.append((km, kmi))
        km = kc.keymaps.new(name = "Property Editor", space_type='PROPERTIES')
        kmi = km.keymap_items.new("korean.properties", type = 'F2', value = 'PRESS')
        addon_keymaps.append((km, kmi))
        km = kc.keymaps.new(name = "Window")
        kmi = km.keymap_items.new("korean.textfield", type = 'F2', value = 'PRESS')
        addon_keymaps.append((km, kmi))
        km = kc.keymaps.new(name = "NLA Editor", space_type='NLA_EDITOR')
        kmi = km.keymap_items.new("korean.nonlinear", type = 'F2', value = 'PRESS')
        addon_keymaps.append((km, kmi))
        km = kc.keymaps.new(name = "Sequencer", space_type='SEQUENCE_EDITOR')
        kmi = km.keymap_items.new("korean.sequencer", type = 'F2', value = 'PRESS')
        addon_keymaps.append((km, kmi))
        km = kc.keymaps.new(name = "File Browser", space_type='FILE_BROWSER')
        kmi = km.keymap_items.new("korean.browser", type = 'F2', value = 'PRESS')
        addon_keymaps.append((km, kmi))
        km = kc.keymaps.new(name = "Text", space_type='TEXT_EDITOR')
        kmi = km.keymap_items.new("korean.text_editor", type = 'F2', value = 'PRESS')
        addon_keymaps.append((km, kmi))
        km = kc.keymaps.new(name = "Text Generic", space_type='TEXT_EDITOR')
        kmi = km.keymap_items.new("korean.text_find", type = 'F', value = 'PRESS', ctrl=True)
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
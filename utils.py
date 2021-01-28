import bpy

class Utils:
    @staticmethod
    def Redraw():
        for area in bpy.context.window.screen.areas:
            area.tag_redraw()

    @staticmethod
    def MessageBox(context, message = "", title = "Message Box", icon = 'INFO'):
        def draw(self, context):
            self.layout.label(text=message)
        context.window_manager.popup_menu(draw, title = title, icon = icon)

import bpy
import gpu
from gpu_extras.batch import batch_for_shader

class GPU:
    @staticmethod
    def DrawRect(x, y, w, h, color=(1, 1, 1, 1)):
        vertices = ((x, y), (x+w, y), (x, y+h), (x+w, y+h))
        indices = ((0, 1, 2), (2, 1, 3))

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

        shader.bind()
        shader.uniform_float("color", color)
        batch.draw(shader)

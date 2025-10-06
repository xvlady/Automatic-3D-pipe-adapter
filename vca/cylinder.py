import numpy as np
import trimesh
from trimesh import Trimesh

from text import text_3d


def create_hollow_cylinder(r_outer, r_inner, height, segments=64, y_offset=0) -> Trimesh:

    vertices = []
    angles = np.linspace(0, 2 * np.pi, segments, endpoint=False)

    # Наружные окружности (низ и верх)
    for y in [y_offset, y_offset + height]:
        for angle in angles:
            x = r_outer * np.cos(angle)
            z = r_outer * np.sin(angle)
            vertices.append([x, y, z])

    # Внутренние окружности (низ и верх)
    for y in [y_offset, y_offset + height]:
        for angle in angles:
            x = r_inner * np.cos(angle)
            z = r_inner * np.sin(angle)
            vertices.append([x, y, z])

    vertices = np.array(vertices)
    circle_points = segments
    faces = []

    def quad_to_triangles(v1, v2, v3, v4):
        return [[v1, v2, v3], [v1, v3, v4]]

    # Внешняя стенка
    for i in range(circle_points):
        next_i = (i + 1) % circle_points
        bottom1 = i
        top1 = i + circle_points
        bottom2 = next_i
        top2 = next_i + circle_points
        faces.extend(quad_to_triangles(bottom1, bottom2, top2, top1))

    # Внутренняя стенка (нормали внутрь — порядок вершин инвертирован)
    offset_inner_bottom = 2 * circle_points
    offset_inner_top = 3 * circle_points
    for i in range(circle_points):
        next_i = (i + 1) % circle_points
        bottom1 = offset_inner_bottom + i
        top1 = offset_inner_top + i
        bottom2 = offset_inner_bottom + next_i
        top2 = offset_inner_top + next_i
        faces.extend(quad_to_triangles(bottom1, top1, top2, bottom2))

    # Верхняя крышка (кольцо между внешним и внутренним радиусом)
    for i in range(circle_points):
        next_i = (i + 1) % circle_points
        outer_top1 = circle_points + i
        outer_top2 = circle_points + next_i
        inner_top1 = 3 * circle_points + i
        inner_top2 = 3 * circle_points + next_i
        faces.extend(quad_to_triangles(outer_top1, outer_top2, inner_top2, inner_top1))

    # Нижняя крышка
    for i in range(circle_points):
        next_i = (i + 1) % circle_points
        outer_bottom1 = i
        outer_bottom2 = next_i
        inner_bottom1 = 2 * circle_points + i
        inner_bottom2 = 2 * circle_points + next_i
        faces.extend(quad_to_triangles(outer_bottom1, outer_bottom2, inner_bottom2, inner_bottom1))

    faces = np.array(faces)
    return Trimesh(vertices=vertices, faces=faces)


def create_embossed_text_on_cylinder(text, r_outer, extrude_depth, height, y_offset=0, font_size=3.0) -> Trimesh:
    text_mesh = text_3d(text, font_size, extrude_height=extrude_depth)
    text_mesh.export('text_mesh.stl')

    verts = text_mesh.vertices.copy()

    # 2. Центрируем текст по X
    min_x = verts[:, 0].min()
    verts[:, 0] -= min_x

    # 3. Масштабируем по длине окружности
    text_width = verts[:, 0].max() - verts[:, 0].min()
    circumference = 2 * np.pi * r_outer
    scale = min(1.0, circumference / (text_width * 1.1))
    verts[:, 0] *= scale

    # 4. Преобразуем X → угол → (x, z) на цилиндре РАДИУСОМ (r_outer)
    theta = verts[:, 0] / r_outer
    x_cyl = r_outer * np.cos(theta)
    z_cyl = r_outer * np.sin(theta)

    # 5. Позиционируем по высоте (по центру)
    y_center = y_offset + height / 2
    y_text_center = (verts[:, 1].max() + verts[:, 1].min()) / 2
    y_new = y_center + (verts[:, 1] - y_text_center)

    # 6. ВАЖНО: смещаем текст ВНУТРЬ на engrave_depth
    # Нормаль к поверхности цилиндра — радиальная: (x, 0, z) → направление от центра
    radial_norm = np.column_stack([x_cyl, np.zeros_like(x_cyl), z_cyl])
    radial_norm /= np.linalg.norm(radial_norm, axis=1, keepdims=True)  # нормализуем

    # Смещаем КАЖДУЮ вершину ВНУТРЬ на engrave_depth
    x_final = x_cyl + radial_norm[:, 0] * extrude_depth
    z_final = z_cyl + radial_norm[:, 2] * extrude_depth

    # 7. Собираем финальные вершины
    final_vertices = np.column_stack([x_final, y_new, z_final])

    embossed_mesh = Trimesh(vertices=final_vertices, faces=text_mesh.faces)
    embossed_mesh.fix_normals()
    return embossed_mesh
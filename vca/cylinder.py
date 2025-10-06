import numpy as np
from stl.mesh import Mesh


def create_hollow_cylinder(d_outer, wall_thickness, height, segments=64, y_offset=0):
    d_inner = d_outer - 2 * wall_thickness
    if d_inner <= 0:
        raise ValueError("Толщина стенки слишком велика, внутренний диаметр <= 0")

    r_outer = d_outer / 2
    r_inner = d_inner / 2

    vertices = []
    angles = np.linspace(0, 2 * np.pi, segments, endpoint=False)

    # Наружные окружности
    for y in [y_offset, y_offset + height]:
        for angle in angles:
            x = r_outer * np.cos(angle)
            z = r_outer * np.sin(angle)
            vertices.append([x, y, z])

    # Внутренние окружности
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

    # Внутренняя стенка
    offset_inner_bottom = 2 * circle_points
    offset_inner_top = 3 * circle_points
    for i in range(circle_points):
        next_i = (i + 1) % circle_points
        bottom1 = offset_inner_bottom + i
        top1 = offset_inner_top + i
        bottom2 = offset_inner_bottom + next_i
        top2 = offset_inner_top + next_i
        # инвертируем порядок для нормалей внутрь
        faces.extend(quad_to_triangles(bottom1, top1, top2, bottom2))

    # Верх крышки
    for i in range(circle_points):
        next_i = (i + 1) % circle_points
        outer_top1 = circle_points + i
        outer_top2 = circle_points + next_i
        inner_top1 = 3 * circle_points + i
        inner_top2 = 3 * circle_points + next_i
        faces.extend(quad_to_triangles(outer_top1, outer_top2, inner_top2, inner_top1))

    # Низ крышки
    for i in range(circle_points):
        next_i = (i + 1) % circle_points
        outer_bottom1 = i
        outer_bottom2 = next_i
        inner_bottom1 = 2 * circle_points + i
        inner_bottom2 = 2 * circle_points + next_i
        faces.extend(quad_to_triangles(outer_bottom1, inner_bottom1, inner_bottom2, outer_bottom2))

    faces = np.array(faces)
    hollow_cylinder = Mesh(np.zeros(faces.shape[0], dtype=Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            hollow_cylinder.vectors[i][j] = vertices[f[j]]
    return hollow_cylinder

import numpy as np
from stl import mesh

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
    hollow_cylinder = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            hollow_cylinder.vectors[i][j] = vertices[f[j]]
    return hollow_cylinder


def create_hollow_cone_with_wall_thickness(d_base_outer, d_top_outer, height, wall_thickness,
                                           center_x=0, center_z=0, y_base=0, segments=64, cut_height=None):
    r_base_outer = d_base_outer / 2
    r_top_outer = d_top_outer / 2

    if cut_height is None or cut_height > height:
        cut_height = height

    y_cut = y_base + cut_height

    angles = np.linspace(0, 2 * np.pi, segments, endpoint=False)

    # Радиусы на срезе (cut)
    r_cut = r_base_outer + (r_top_outer - r_base_outer) * (cut_height / height)

    outer_base_ring = []
    outer_cut_ring = []

    # Создаем внешнюю поверхность: внешний радиус
    for angle in angles:
        x_base = center_x + r_base_outer * np.cos(angle)
        z_base = center_z + r_base_outer * np.sin(angle)
        outer_base_ring.append(np.array([x_base, y_base, z_base]))

        x_cut = center_x + r_cut * np.cos(angle)
        z_cut = center_z + r_cut * np.sin(angle)
        outer_cut_ring.append(np.array([x_cut, y_cut, z_cut]))

    # Внутренний радиус — по условию, чтобы толщина по горизонтали равнялась z
    r_base_inner = r_base_outer - z
    r_cut_inner = r_cut - z

    inner_base_ring = []
    inner_cut_ring = []

    for angle in angles:
        # Внутренние точки на основании и срезе
        x_base_inner = center_x + r_base_inner * np.cos(angle)
        z_base_inner = center_z + r_base_inner * np.sin(angle)
        inner_base_ring.append(np.array([x_base_inner, y_base, z_base_inner]))

        x_cut_inner = center_x + r_cut_inner * np.cos(angle)
        z_cut_inner = center_z + r_cut_inner * np.sin(angle)
        inner_cut_ring.append(np.array([x_cut_inner, y_cut, z_cut_inner]))

    # Собираем вершины
    vertices = np.array(outer_base_ring + outer_cut_ring + inner_base_ring + inner_cut_ring)
    s = segments
    faces = []

    # Формируем стороны боковой поверхности
    for i in range(s):
        next_i = (i + 1) % s
        # Внешняя боковая поверхность
        faces.append([i, next_i, s + next_i])
        faces.append([i, s + next_i, s + i])
        # Внутренняя боковая поверхность (нормали внутрь, инвертируем порядок)
        a = 2 * s + i
        b = 2 * s + next_i
        c = 3 * s + next_i
        d = 3 * s + i
        faces.append([a, c, b])
        faces.append([a, d, c])
        # Основание — внутренний и внешний круг
        faces.append([i, 2 * s + i, 2 * s + next_i])
        faces.append([i, 2 * s + next_i, next_i])
        # Верхние крышки (среза)
        faces.append([s + i, 3 * s + i, 3 * s + next_i])
        faces.append([s + i, 3 * s + next_i, s + next_i])

    faces = np.array(faces)

    mesh_obj = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            mesh_obj.vectors[i][j] = vertices[f[j]]

    return mesh_obj


if __name__ == '__main__':
    print("Параметры цилиндра большого в мм")
    print("диаметр внешний в мм")
    x = int(input())
    print("длина в мм")
    c = int(input())
    # Параметры цилиндров
    # c = 20
    # z = 1
    # x = 10
    print("Параметры цилиндра малого")
    print("диаметр внешний")
    x2 = int(input())
    print("длина")
    c2 = int(input())
    print("Параметры цилиндра всех")
    print("толщина стенок")
    z = int(input())
    z2 = z
    # Параметры цилиндров
    #x2 = 5
    #z2 = 1
    #c2 = 20
    # Создаем конус между цилиндрами
    x3 = x  # конус между цилиндрами
    z3 = x - 2 * z  # - конус между цилиндрами
    cone_height = (x3 * (3 ** 0.5)) / 2  # Высота конуса
    z123=z**2
    c3 =((x-x2)/2)+(3**0.5)
    c4=c3+z/2+z
    f12=cone_height-c4
    c22 = c4 + c
    cylinder1 = create_hollow_cylinder(d_outer=x, wall_thickness=z, height=c, y_offset=0)
    cylinder2 = create_hollow_cylinder(d_outer=x2, wall_thickness=z2, height=c2, y_offset=c22)

    # Вершина конуса сверху на высоте c + cone_height
    cone_mesh = create_hollow_cone_with_wall_thickness(
        d_base_outer=x,  # наружный диаметр основания
        d_top_outer=x2,  # наружный диаметр вершины
        height=c4,  # высота
        wall_thickness=z123,  # толщина стенки в направлении X
        center_x=0,
        center_z=0,
        y_base=c,
        segments=64,
        cut_height=c4 # усечь конус на c4
    )

    # Объединяем все
    combined_data = mesh.Mesh(np.concatenate([cylinder1.data, cone_mesh.data, cylinder2.data]))

    combined_data.save(f'vacuum_cleaner_adapter_{x}_{x2}.stl')
    print(f'vacuum_cleaner_adapter_{x}_{x2}.stl')
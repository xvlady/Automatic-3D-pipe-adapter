import numpy as np
import trimesh
from trimesh import Trimesh
from trimesh import transformations as tf
from trimesh.util import concatenate

from con_mesh import ConMesh
from cone import create_hollow_cone_with_wall_thickness
from cylinder import create_embossed_text_on_cylinder
from cylinder import create_hollow_cylinder
from picture import generate_cross_section_from_mesh


def create_adapter(con: ConMesh, len_cylinder: float):
    cylinder1 = create_hollow_cylinder(con.r_base_outer, con.r_base_inner, len_cylinder, segments=128, y_offset=0)
    # Создаём гравировку
    engraving = create_embossed_text_on_cylinder(
        text=con.text,
        r_outer=con.r_base_outer,
        extrude_depth=con.engrave_depth,
        height=len_cylinder,
        y_offset=0,
        font_size=10.0
    )
    engraving.export('graftryhtrywr.stl')

    cylinder2 = create_hollow_cylinder(con.r_top_outer, con.r_top_inner, len_cylinder, segments=128, y_offset=con.height + len_cylinder)

    # Вершина конуса сверху на высоте c + cone_height
    cone_mesh = create_hollow_cone_with_wall_thickness(
        con=con,
        center_x=0,
        center_z=0,
        y_base=len_cylinder,
        segments=128,
        cut_height=con.height  # усечь конус на c4
    )
    # Объединяем все
    combined_data = concatenate([cylinder1, engraving, cone_mesh, cylinder2])
    transform = tf.rotation_matrix(np.pi / 2, [1, 0, 0])  # +90° вокруг X
    combined_data.apply_transform(transform)

    return combined_data

def generate_stl(d_cylinder1: float, d_cylinder2: float, thickness: float, len_cylinder: float) -> None:
    con = ConMesh(d_cylinder1, d_cylinder2, thickness_cylinder=thickness)

    combined_data = create_adapter(con, len_cylinder)
    combined_data.export(f'vacuum_cleaner_adapter_{d_cylinder1}_{d_cylinder2}.stl', file_type='stl_ascii')

    # Генерируем сечение ИЗ МОДЕЛИ
    # generate_cross_section_from_mesh(
    #     combined_data,
    #     cut_plane_normal=[1, 0, 0],   # режем плоскостью X=0
    #     cut_plane_origin=[0, 0, 0],
    #     filename="cylinder_section_from_mesh.png"
    # )
    print(f'vacuum_cleaner_adapter_{d_cylinder1}_{d_cylinder2}.stl')

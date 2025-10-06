import numpy as np
from stl import Mesh
from trimesh import Trimesh
from trimesh import transformations as tf
from trimesh.util import concatenate

from con_mesh import ConMesh
from cone import create_hollow_cone_with_wall_thickness
from cylinder import create_hollow_cylinder
from picture import generate_cross_section_from_mesh


def stl_mesh_to_trimesh(stl_obj):
    """Конвертирует stl.mesh.Mesh → trimesh.Trimesh"""
    return Trimesh(
        vertices=stl_obj.vectors.reshape(-1, 3),
        faces=np.arange(stl_obj.vectors.size // 3).reshape(-1, 3)
    )

def create_adapter(con: ConMesh, len_cylinder: float):
    cylinder1 = create_hollow_cylinder(
        d_outer=con.d_base_outer, wall_thickness=con.thickness_cylinder, height=len_cylinder, y_offset=0
    )
    cylinder2 = create_hollow_cylinder(
        d_outer=con.d_top_outer, wall_thickness=con.thickness_cylinder, height=len_cylinder,
                                       y_offset=con.height + len_cylinder
    )

    # Вершина конуса сверху на высоте c + cone_height
    cone_mesh = create_hollow_cone_with_wall_thickness(
        con=con,
        center_x=0,
        center_z=0,
        y_base=len_cylinder,
        segments=64,
        cut_height=con.height  # усечь конус на c4
    )

    # Объединяем все
    combined_data = concatenate(list(map(stl_mesh_to_trimesh, [cylinder1, cone_mesh, cylinder2])))
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

import os
import unittest

from adapter import generate_stl
from con_mesh import ConMesh
from text import text_3d


class TestGenerateSTL(unittest.TestCase):
    test_filename = ''

    def test_text(self):
        self.assertEqual(ConMesh(37.0, 39.0, 2).text, '39 x 33')
        self.assertEqual(ConMesh(37.06, 39.04, 2).text, '39 x 33')
        self.assertEqual(ConMesh(37.6, 39.4, 2).text, '39.6 x 33.4')

    def test_stl_generation(self):
        """Тест: генерация STL-файла"""
        r_cylinder1 = 39
        r_cylinder2 = 37
        thickness = 2.0
        len_cylinder = 30.0

        self.test_filename = f'vacuum_cleaner_adapter_{r_cylinder1}_{r_cylinder2}.stl'

        # Удаляем файл, если он существует
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

        # Вызываем функцию
        generate_stl(r_cylinder1, r_cylinder2, thickness, len_cylinder)

        # Проверяем, что файл создан
        self.assertTrue(os.path.exists(self.test_filename), "Файл STL не был создан")

        # Проверяем, что файл не пустой
        self.assertGreater(os.path.getsize(self.test_filename), 0, "Файл STL пустой")

    def test_cross_section_generation(self):
        r_cylinder1 = 39
        r_cylinder2 = 37
        thickness = 2.0
        len_cylinder = 30.0
        self.test_filename = f'vacuum_cleaner_adapter_{r_cylinder1}_{r_cylinder2}.stl'
        """Тест: генерация сечения из модели"""
        # Удаляем файл сечения, если он существует
        section_filename = "cylinder_section_from_mesh.png"
        if os.path.exists(section_filename):
            os.remove(section_filename)

        # Вызываем функцию
        generate_stl(r_cylinder1, r_cylinder2, thickness, len_cylinder)

        # Проверяем, что файл сечения создан
        self.assertTrue(os.path.exists(section_filename), "Файл сечения не был создан")

        # Проверяем, что файл не пустой
        self.assertGreater(os.path.getsize(section_filename), 0, "Файл сечения пустой")

    # def tearDown(self):
    #     # Удаляем временные файлы после тестов
    #     if self.test_filename and os.path.exists(self.test_filename):
    #         os.remove(self.test_filename)
    #     if os.path.exists("cylinder_section_from_mesh.png"):
    #         os.remove("cylinder_section_from_mesh.png")

    def test_text_3d(self):
        mesh = text_3d('2')
        output_file = "digits_1234_manual.stl"
        mesh.export(output_file)

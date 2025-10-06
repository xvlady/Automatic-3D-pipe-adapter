class ConMesh:
    d_base_outer: float
    d_top_outer: float
    thickness_cylinder: float
    engrave_depth: float = 1

    def __init__(
            self,
            d_base_outer: float,
            d_top_outer: float,
            thickness_cylinder: float,
    ):
        if d_base_outer > d_top_outer:
            self.d_base_outer, self.d_top_outer = d_base_outer, d_top_outer
        else:
            self.d_base_outer, self.d_top_outer = d_top_outer, d_base_outer

        if thickness_cylinder > d_top_outer:
            raise ValueError("Толщина стенки слишком велика, внутренний диаметр <= 0")

        self.thickness_cylinder = thickness_cylinder

    @property
    def r1_internal(self) -> float:
        return self.d_base_outer - 2 * self.thickness_cylinder

    @property
    def height_out1(self) -> float:
        return (self.d_base_outer * (3 ** 0.5)) / 2  # Высота внешнего конуса

    @property
    def height(self) -> float:
        c3 = ((self.d_base_outer - self.d_top_outer) / 2) + (3 ** 0.5)
        return c3 + self.thickness_cylinder / 2 + self.thickness_cylinder

    @property
    def thickness(self) -> float:
        return self.thickness_cylinder ** 2

    @property
    def r_base_outer(self) -> float:
        return self.d_base_outer / 2

    @property
    def r_top_outer(self) -> float:
        return self.d_top_outer / 2

    @property
    def r_base_inner(self) -> float:
        return self.r_base_outer - self.thickness_cylinder

    @property
    def r_top_inner(self) -> float:
        return self.r_top_outer - self.thickness_cylinder

    @property
    def d_base_inner(self) -> float:
        return self.d_base_outer - 2 * self.thickness_cylinder

    @property
    def d_top_inner(self) -> float:
        return self.d_top_outer - 2 * self.thickness_cylinder

    @property
    def text(self) ->  str:
        return f'{self.d_base_inner} x {self.d_top_outer}'
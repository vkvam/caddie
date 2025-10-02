import unittest

from caddie.plane import Plane, Translation, Rotation, AXIS_X


class TestPlane(unittest.TestCase):

    def test_independent_copy(self):
        p0 = Plane()
        p1 = p0.transformed(Translation(0,0,0))
        p2 = p0.transformed(Translation(1,0,0))
        p3 = p0.transformed(Rotation(1, AXIS_X))

        assert p0 is not p1
        assert p0 is not p2
        assert p0 is not p3

        assert p0.o is not p1.o
        assert p0.o is not p2.o
        assert p0.o is not p3.o

        assert p0.o == p1.o
        assert p0.o != p2.o
        assert p0.o == p3.o

        assert p0.n == p1.n
        assert p0.n == p2.n
        assert p0.n != p3.n


import numpy as np
from collections import defaultdict

from sverchok.utils.geom import Spline
from sverchok.utils.nurbs_common import (
        SvNurbsMaths, SvNurbsBasisFunctions,
        nurbs_divide, from_homogenous
    )
from sverchok.utils.curve import knotvector as sv_knotvector
from sverchok.utils.curve.nurbs_algorithms import interpolate_nurbs_curve, unify_curves, nurbs_curve_to_xoy, nurbs_curve_matrix
from sverchok.utils.curve.algorithms import unify_curves_degree, SvCurveFrameCalculator
from sverchok.utils.surface.core import UnsupportedSurfaceTypeException
from sverchok.utils.surface import SvSurface, SurfaceCurvatureCalculator, SurfaceDerivativesData
from sverchok.utils.surface.nurbs import SvNurbsSurface, simple_loft, interpolate_nurbs_surface
from sverchok.utils.surface.algorithms import unify_nurbs_surfaces
from sverchok.data_structure import repeat_last_for_length

def gordon_surface_impl(u_curves, v_curves, intersections, metric='DISTANCE'):

    #u_curves = [c.reparametrize(0.0, 1.0) for c in u_curves]
    #v_curves = [c.reparametrize(0.0, 1.0) for c in v_curves]

    intersections = np.asarray(intersections)

    n = len(intersections)
    m = len(intersections[0])

    knots = np.array([Spline.create_knots(intersections[i,:], metric=metric) for i in range(n)])
    u_knots = knots.mean(axis=0)

    knots = np.array([Spline.create_knots(intersections[:,j], metric=metric) for j in range(m)])
    v_knots = knots.mean(axis=0)

    loft_v_degree = len(u_curves)-1
    loft_u_degree = len(v_curves)-1

    _,_,lofted_v = simple_loft(u_curves, degree_v=loft_v_degree, tknots=u_knots)
    _,_,lofted_u = simple_loft(v_curves, degree_v=loft_u_degree, tknots=v_knots)
    lofted_u = lofted_u.swap_uv()

    int_degree_u = m-1
    int_degree_v = n-1
    interpolated = interpolate_nurbs_surface(int_degree_u, int_degree_v, intersections, uknots=u_knots, vknots=v_knots)
    interpolated = interpolated.swap_uv()
    #print(f"Loft.U: {lofted_u}")
    #print(f"Loft.V: {lofted_v}")
    #print(f"Interp: {interpolated}")
    #print(f"        {interpolated.get_knotvector_u()}")
    #print(f"        {interpolated.get_knotvector_v()}")

    lofted_u, lofted_v, interpolated = unify_nurbs_surfaces([lofted_u, lofted_v, interpolated])

    control_points = lofted_u.get_control_points() + \
                        lofted_v.get_control_points() - \
                        interpolated.get_control_points()

    surface = SvNurbsSurface.build(SvNurbsSurface.NATIVE,
                interpolated.get_degree_u(), interpolated.get_degree_v(),
                interpolated.get_knotvector_u(), interpolated.get_knotvector_v(),
                control_points, weights=None)
    #print(f"Result: {surface}")

    return lofted_u, lofted_v, interpolated, surface
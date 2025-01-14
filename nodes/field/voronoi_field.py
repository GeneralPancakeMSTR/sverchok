import numpy as np

import bpy
from bpy.props import FloatProperty, EnumProperty, BoolProperty, IntProperty, StringProperty

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, zip_long_repeat, match_long_repeat

from sverchok.utils.field.scalar import SvVoronoiScalarField
from sverchok.utils.field.vector import SvVoronoiVectorField
from sverchok.utils.field.voronoi import SvVoronoiFieldData

class SvVoronoiFieldNode(SverchCustomTreeNode, bpy.types.Node):
    """
    Triggers: Voronoi Field
    Tooltip: Generate Voronoi field
    """
    bl_idname = 'SvExVoronoiFieldNode'
    bl_label = 'Voronoi Field'
    bl_icon = 'OUTLINER_OB_EMPTY'
    sv_icon = 'SV_VORONOI'

    metrics = [
            ('DISTANCE', 'Euclidan', "Eudlcian distance metric", 0),
            ('MANHATTAN', 'Manhattan', "Manhattan distance metric", 1),
            ('CHEBYSHEV', 'Chebyshev', "Chebyshev distance", 2),
            ('CUSTOM', "Custom", "Custom Minkowski metric defined by exponent factor", 3)
        ]

    metric : EnumProperty(
            name = "Metric",
            items = metrics,
            default = 'DISTANCE',
            update = updateNode)

    power : FloatProperty(
            name = "Exponent",
            description = "Exponent for Minkowski metric",
            min = 1.0,
            default = 2,
            update = updateNode)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'metric')
        if self.metric == 'CUSTOM':
            layout.prop(self, 'power')

    def sv_init(self, context):
        self.inputs.new('SvVerticesSocket', "Vertices")
        self.outputs.new('SvScalarFieldSocket', "SField")
        self.outputs.new('SvVectorFieldSocket', "VField")

    def process(self):

        if not any(socket.is_linked for socket in self.outputs):
            return

        vertices_s = self.inputs['Vertices'].sv_get()

        sfields_out = []
        vfields_out = []
        for vertices in vertices_s:
            data = SvVoronoiFieldData(vertices, metric=self.metric, power=self.power)
            sfield = SvVoronoiScalarField(voronoi=data)
            vfield = SvVoronoiVectorField(voronoi=data)
            sfields_out.append(sfield)
            vfields_out.append(vfield)

        self.outputs['SField'].sv_set(sfields_out)
        self.outputs['VField'].sv_set(vfields_out)

def register():
    bpy.utils.register_class(SvVoronoiFieldNode)

def unregister():
    bpy.utils.unregister_class(SvVoronoiFieldNode)


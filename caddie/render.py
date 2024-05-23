import base64
import json
import math
import tempfile
import os
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepTools import breptools
from OCC.Core.Message import Message_ProgressRange
from OCC.Core.RWGltf import RWGltf_WriterTrsfFormat, RWGltf_CafWriter
from OCC.Core.TColStd import TColStd_IndexedDataMapOfStringString
from OCC.Core.TCollection import TCollection_AsciiString, TCollection_ExtendedString
from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity


def write_gltf_file(a_shape, gltf_filename, linear_deflect=0.1, angular_deflect=0.5):
    """ocaf based ply exporter"""
    # create a document
    doc = TDocStd_Document("pythonocc-doc-gltf-export")
    shape_tool = XCAFDoc_DocumentTool.ShapeTool(doc.Main())

    # mesh shape
    breptools.Clean(a_shape)
    msh_algo = BRepMesh_IncrementalMesh(a_shape, linear_deflect, True, angular_deflect, False)

    msh_algo.Perform()

    shape_tool.AddShape(a_shape)

    # metadata
    a_file_info = TColStd_IndexedDataMapOfStringString()
    a_file_info.Add(
        TCollection_AsciiString("Authors"), TCollection_AsciiString("pythonocc")
    )

    rwgltf_writer = RWGltf_CafWriter(gltf_filename, False)

    status = rwgltf_writer.Perform(doc, a_file_info, Message_ProgressRange())

    if status != IFSelect_RetDone:
        raise IOError("Error while writing shape to STEP file.")


def shape_to_gltf(shape, linear_deflect=0.01, angular_deflect=0.125):
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmp_src = os.path.join(tmpdirname, 'box.gltf')
        write_gltf_file(shape, tmp_src, linear_deflect, angular_deflect)
        with open(tmp_src, "rb") as f2:
            dat = f2.read()
            gltf_data = json.loads(dat)
            tmp_bin = os.path.join(tmpdirname, gltf_data['buffers'][0]['uri'])

            with open(tmp_bin, 'rb') as f3:
                bin_data = f3.read()
                base64_data = base64.b64encode(bin_data).decode('utf-8')
                gltf_data['buffers'][0]['uri'] = f"data:application/octet-stream;base64,{base64_data}"
                return json.dumps(gltf_data)

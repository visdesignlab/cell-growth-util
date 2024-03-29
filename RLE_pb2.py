# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: RLE.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='RLE.proto',
  package='imageLabels',
  syntax='proto2',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\tRLE.proto\x12\x0bimageLabels\"0\n\x0bImageLabels\x12!\n\x07rowList\x18\x01 \x03(\x0b\x32\x10.imageLabels.Row\")\n\x03Row\x12\"\n\x03row\x18\x01 \x03(\x0b\x32\x15.imageLabels.LabelRun\"8\n\x08LabelRun\x12\r\n\x05start\x18\x01 \x02(\x05\x12\x0e\n\x06length\x18\x02 \x02(\x05\x12\r\n\x05label\x18\x03 \x02(\x05'
)




_IMAGELABELS = _descriptor.Descriptor(
  name='ImageLabels',
  full_name='imageLabels.ImageLabels',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='rowList', full_name='imageLabels.ImageLabels.rowList', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=26,
  serialized_end=74,
)


_ROW = _descriptor.Descriptor(
  name='Row',
  full_name='imageLabels.Row',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='row', full_name='imageLabels.Row.row', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=76,
  serialized_end=117,
)


_LABELRUN = _descriptor.Descriptor(
  name='LabelRun',
  full_name='imageLabels.LabelRun',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='start', full_name='imageLabels.LabelRun.start', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='length', full_name='imageLabels.LabelRun.length', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='label', full_name='imageLabels.LabelRun.label', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=119,
  serialized_end=175,
)

_IMAGELABELS.fields_by_name['rowList'].message_type = _ROW
_ROW.fields_by_name['row'].message_type = _LABELRUN
DESCRIPTOR.message_types_by_name['ImageLabels'] = _IMAGELABELS
DESCRIPTOR.message_types_by_name['Row'] = _ROW
DESCRIPTOR.message_types_by_name['LabelRun'] = _LABELRUN
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ImageLabels = _reflection.GeneratedProtocolMessageType('ImageLabels', (_message.Message,), {
  'DESCRIPTOR' : _IMAGELABELS,
  '__module__' : 'RLE_pb2'
  # @@protoc_insertion_point(class_scope:imageLabels.ImageLabels)
  })
_sym_db.RegisterMessage(ImageLabels)

Row = _reflection.GeneratedProtocolMessageType('Row', (_message.Message,), {
  'DESCRIPTOR' : _ROW,
  '__module__' : 'RLE_pb2'
  # @@protoc_insertion_point(class_scope:imageLabels.Row)
  })
_sym_db.RegisterMessage(Row)

LabelRun = _reflection.GeneratedProtocolMessageType('LabelRun', (_message.Message,), {
  'DESCRIPTOR' : _LABELRUN,
  '__module__' : 'RLE_pb2'
  # @@protoc_insertion_point(class_scope:imageLabels.LabelRun)
  })
_sym_db.RegisterMessage(LabelRun)


# @@protoc_insertion_point(module_scope)

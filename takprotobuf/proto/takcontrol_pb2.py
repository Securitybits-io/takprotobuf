# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: takcontrol.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='takcontrol.proto',
  package='',
  syntax='proto3',
  serialized_options=_b('H\003'),
  serialized_pb=_b('\n\x10takcontrol.proto\"R\n\nTakControl\x12\x17\n\x0fminProtoVersion\x18\x01 \x01(\r\x12\x17\n\x0fmaxProtoVersion\x18\x02 \x01(\r\x12\x12\n\ncontactUid\x18\x03 \x01(\tB\x02H\x03\x62\x06proto3')
)




_TAKCONTROL = _descriptor.Descriptor(
  name='TakControl',
  full_name='TakControl',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='minProtoVersion', full_name='TakControl.minProtoVersion', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='maxProtoVersion', full_name='TakControl.maxProtoVersion', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='contactUid', full_name='TakControl.contactUid', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=20,
  serialized_end=102,
)

DESCRIPTOR.message_types_by_name['TakControl'] = _TAKCONTROL
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

TakControl = _reflection.GeneratedProtocolMessageType('TakControl', (_message.Message,), dict(
  DESCRIPTOR = _TAKCONTROL,
  __module__ = 'takcontrol_pb2'
  # @@protoc_insertion_point(class_scope:TakControl)
  ))
_sym_db.RegisterMessage(TakControl)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
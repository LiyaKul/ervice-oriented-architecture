# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: engine.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0c\x65ngine.proto\"E\n\x0bJoinRequest\x12\x11\n\x04name\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x11\n\x04text\x18\x02 \x01(\tH\x01\x88\x01\x01\x42\x07\n\x05_nameB\x07\n\x05_text\"6\n\x0cJoinResponse\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x11\n\x04text\x18\x02 \x01(\tH\x00\x88\x01\x01\x42\x07\n\x05_text\"=\n\x11GetPlayersRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\x04text\x18\x02 \x01(\tH\x00\x88\x01\x01\x42\x07\n\x05_text\"N\n\x12GetPlayersResponse\x12\r\n\x05\x63ount\x18\x01 \x01(\x05\x12\r\n\x05names\x18\x02 \x01(\t\x12\x11\n\x04text\x18\x03 \x01(\tH\x00\x88\x01\x01\x42\x07\n\x05_text\"8\n\x0cStartRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\x04text\x18\x02 \x01(\tH\x00\x88\x01\x01\x42\x07\n\x05_text\"x\n\rStartResponse\x12\x0f\n\x07started\x18\x01 \x01(\x08\x12\x11\n\x04role\x18\x02 \x01(\tH\x00\x88\x01\x01\x12\x11\n\x04text\x18\x03 \x01(\tH\x01\x88\x01\x01\x12\x13\n\x06mafias\x18\x04 \x01(\tH\x02\x88\x01\x01\x42\x07\n\x05_roleB\x07\n\x05_textB\t\n\x07_mafias\"7\n\x0bInfoRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\x04text\x18\x02 \x01(\tH\x00\x88\x01\x01\x42\x07\n\x05_text\"\x1c\n\x0cInfoResponse\x12\x0c\n\x04text\x18\x01 \x01(\t\"\xa5\x01\n\rActionRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\x04text\x18\x02 \x01(\tH\x00\x88\x01\x01\x12\x11\n\x04type\x18\x03 \x01(\tH\x01\x88\x01\x01\x12\x16\n\tvote_name\x18\x04 \x01(\tH\x02\x88\x01\x01\x12\x18\n\x0b\x61\x63tion_name\x18\x05 \x01(\tH\x03\x88\x01\x01\x42\x07\n\x05_textB\x07\n\x05_typeB\x0c\n\n_vote_nameB\x0e\n\x0c_action_name\"\x84\x01\n\x0e\x41\x63tionResponse\x12\x11\n\x04text\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x11\n\x04type\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x11\n\x04name\x18\x03 \x01(\tH\x02\x88\x01\x01\x12\x13\n\x06mafias\x18\x04 \x01(\tH\x03\x88\x01\x01\x42\x07\n\x05_textB\x07\n\x05_typeB\x07\n\x05_nameB\t\n\x07_mafias2\xfa\x01\n\x0c\x45ngineServer\x12%\n\x04Join\x12\x0c.JoinRequest\x1a\r.JoinResponse\"\x00\x12\x37\n\nGetPlayers\x12\x12.GetPlayersRequest\x1a\x13.GetPlayersResponse\"\x00\x12(\n\x05Start\x12\r.StartRequest\x1a\x0e.StartResponse\"\x00\x12+\n\x08GameInfo\x12\x0c.InfoRequest\x1a\r.InfoResponse\"\x00\x30\x01\x12\x33\n\nGameAction\x12\x0e.ActionRequest\x1a\x0f.ActionResponse\"\x00(\x01\x30\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'engine_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _JOINREQUEST._serialized_start=16
  _JOINREQUEST._serialized_end=85
  _JOINRESPONSE._serialized_start=87
  _JOINRESPONSE._serialized_end=141
  _GETPLAYERSREQUEST._serialized_start=143
  _GETPLAYERSREQUEST._serialized_end=204
  _GETPLAYERSRESPONSE._serialized_start=206
  _GETPLAYERSRESPONSE._serialized_end=284
  _STARTREQUEST._serialized_start=286
  _STARTREQUEST._serialized_end=342
  _STARTRESPONSE._serialized_start=344
  _STARTRESPONSE._serialized_end=464
  _INFOREQUEST._serialized_start=466
  _INFOREQUEST._serialized_end=521
  _INFORESPONSE._serialized_start=523
  _INFORESPONSE._serialized_end=551
  _ACTIONREQUEST._serialized_start=554
  _ACTIONREQUEST._serialized_end=719
  _ACTIONRESPONSE._serialized_start=722
  _ACTIONRESPONSE._serialized_end=854
  _ENGINESERVER._serialized_start=857
  _ENGINESERVER._serialized_end=1107
# @@protoc_insertion_point(module_scope)

import msgpack
import json
import pickle
import sys
import timeit
import xmltodict
import yaml
from dicttoxml import dicttoxml
from google.protobuf import json_format

from support import protodata_pb2 as protodata
from support.other import *
from data_formats.data import data, schema_dict

DATA = data

def get_native():
    data_size = sys.getsizeof(pickle.dumps(DATA))
    ser_time = timeit.timeit(stmt="pickle.dumps(DATA)", number=1000, globals=globals())
    deser_time = timeit.timeit(setup="bytes_data=pickle.dumps(DATA)", stmt="pickle.loads(bytes_data)", number=1000, globals=globals())
    return data_size, ser_time, deser_time

def get_xml():
    data_size = sys.getsizeof(dicttoxml(data))
    ser_time = timeit.timeit(stmt="dicttoxml(DATA)", number=1000, globals=globals())
    deser_time = timeit.timeit(setup="xml_data=dicttoxml(DATA)", stmt="xmltodict.parse(xml_data)", number=1000, globals=globals())
    return data_size, ser_time, deser_time

def get_json():
    data_size = sys.getsizeof(json.dumps(DATA))
    ser_time = timeit.timeit(stmt="json.dumps(DATA)", number=1000, globals=globals())
    deser_time = timeit.timeit(setup="json_data=json.dumps(DATA)", stmt="json.loads(json_data)", number=1000, globals=globals())
    return data_size, ser_time, deser_time

def get_proto():
    proto_data = protodata.Data()
    json_format.ParseDict(data, proto_data)
    data_size = sys.getsizeof(proto_data)
    parse = '''proto_data = protodata.Data()
json_format.ParseDict(DATA, proto_data)'''
    ser_time = timeit.timeit(stmt=parse, number=1000, globals=globals())
    deser_time = timeit.timeit(setup=parse,stmt="json_format.MessageToDict(proto_data)", number=1000, globals=globals())
    return data_size, ser_time, deser_time

def get_avro():
    data_size = sys.getsizeof(serialize(schema_dict, DATA))
    ser_time = timeit.timeit(stmt="serialize(schema_dict, DATA)", number=1000, globals=globals())
    deser_time = timeit.timeit(setup="avro_data=serialize(schema_dict, DATA)", stmt="deserialize(schema_dict, avro_data)", number=1000, globals=globals())
    return data_size, ser_time, deser_time

def get_yaml():
    yaml_data = yaml.dump(DATA)
    data_size = sys.getsizeof(yaml_data)
    ser_time = timeit.timeit(stmt="yaml.dump(DATA)", number=1000, globals=globals())
    deser_time = timeit.timeit(setup="yaml_data=yaml.dump(DATA)", stmt="yaml.safe_load(yaml_data)", number=1000, globals=globals())
    return data_size, ser_time, deser_time

def get_msg_pack():
    data_size = sys.getsizeof(msgpack.packb(DATA))
    ser_time = timeit.timeit(stmt="msgpack.packb(DATA)", number=1000, globals=globals())
    deser_time = timeit.timeit(setup="msg_pack_data=msgpack.packb(DATA)", stmt="msgpack.packb(msg_pack_data)", number=1000, globals=globals())
    return data_size, ser_time, deser_time

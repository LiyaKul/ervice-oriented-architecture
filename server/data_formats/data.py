data = {
    "string": "hello",
    "array": [0, 1, 2, 3, 4, 5],
    "dict": {"Gosha": 20,
             "Liya": 21
            },
    "int": 1000000,
    "float": 0.9999
}

schema_dict = {
    "name": "data",
    "type": "record",
    "fields": [
        {
            "name": "string",
            "type": "string"
        },
        {
            "name": "array",
            "type": {"type": "array", "items": "long"}
        },
        {
            "name": "dict",
            "type": {"type": "map", "values": "long"}
        },
        {
            "name": "int",
            "type": "long"
        },
        {
            "name": "float",
            "type": "double"
        }
    ]
}
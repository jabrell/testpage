# valid and invalid schema under frictionless standard only
fl_valid = {
    "fields": [
        {"name": "id", "type": "integer"},
        {"name": "name", "type": "string"},
    ],
}

fl_invalid = {"name": "test"}

sweet_valid = {
    # schema misses the "name" key which is mandatory in the SWEET standard
    "fields": [
        {"name": "id", "title": "Identifier", "type": "integer"},
        {"name": "name", "title": "Name", "type": "string"},
    ],
    "name": "test",
    "title": "test",
    "description": "test",
    "primaryKey": ["test"],
}

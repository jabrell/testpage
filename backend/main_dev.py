# def test_create_schema(db: Session) -> None:
#     data = str(sweet_valid).encode("utf-8")
#     content_str = data.decode("utf-8")
#     t = yaml.safe_load(content_str)
#     print(t)
#     schema_manger = SchemaManager()
#     schema = create_schema(db=db, data=data, schema_manager=schema_manger)
#     assert schema.name == "test"
#     assert schema.description == "test"
#     assert schema.jsonschema == sweet_valid


if __name__ == "__main__":
    # test_create_schema(db=None)
    print("here")

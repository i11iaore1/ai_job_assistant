from sqlalchemy import DDL

TRIGGER_FUNC_NAME = "update_modified_column"
UPDATED_AT_FIELD_NAME = "updated_at"

create_on_upate_trigger_func = DDL(f"""
    CREATE OR REPLACE FUNCTION {TRIGGER_FUNC_NAME}()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.{UPDATED_AT_FIELD_NAME} = TIMEZONE('utc', now());
        RETURN NEW;
    END;
    $$ language 'plpgsql';
""")


def create_on_update_trigger(trigger_name: str, table_name: str):
    return DDL(f"""
        CREATE TRIGGER {trigger_name}
        BEFORE UPDATE ON {table_name}
        FOR EACH ROW
        EXECUTE PROCEDURE {TRIGGER_FUNC_NAME}();
    """)


# event.listen(User.__table__, "after_create", create_on_upate_trigger_func)
# event.listen(
#     User.__table__,
#     "after_create",
#     create_on_update_trigger(trigger_name="on_update_user", table_name="users"),
# )

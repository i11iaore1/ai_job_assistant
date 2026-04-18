TRIGGER_FUNC_NAME = "update_modified_column"
UPDATED_AT_FIELD_NAME = "updated_at"


def trigger_name(table_name: str):
    return f"on_update_{table_name}"


create_on_update_trigger_func = f"""
    CREATE OR REPLACE FUNCTION {TRIGGER_FUNC_NAME}()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.{UPDATED_AT_FIELD_NAME} = TIMEZONE('utc', now());
        RETURN NEW;
    END;
    $$ language 'plpgsql';
"""

drop_on_update_trigger_func = f"""
    DROP FUNCTION IF EXISTS {TRIGGER_FUNC_NAME}();
"""


def create_on_update_trigger(trigger_name: str, table_name: str):
    return f"""
        CREATE TRIGGER {trigger_name}
        BEFORE UPDATE ON {table_name}
        FOR EACH ROW
        EXECUTE PROCEDURE {TRIGGER_FUNC_NAME}();
    """


def drop_on_update_trigger(trigger_name: str, table_name: str):
    return f"""
        DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};
    """

from sqlalchemy import text


def check_active_connections(engine):
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
        )
        return result.scalar()


def check_for_deadlocks(engine):
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT count(*) FROM pg_locks WHERE granted = false")
        )
        return result.scalar()

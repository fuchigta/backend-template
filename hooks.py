import dredd_hooks as hooks


@hooks.before_all
def setup_database(transactions):
    """Setup database before running tests"""
    pass


@hooks.before_each
def reset_database(transaction):
    """Reset database before each test"""
    pass


@hooks.before("Tasks > /tasks > Create a new task > 201 > application/json")
def before_create_task(transaction):
    """Hook for task creation"""
    pass

def can_visible_dashboard_and_statistics(user):
    if not user.is_superuser and not user.groups.filter(name='Manager').exists() and not user.groups.filter(name='Support').exists():
        return False
    return True


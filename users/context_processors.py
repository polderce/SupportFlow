def user_group_context(request):
    is_super = False
    is_manager = False
    is_support = False
    is_user = False

    if request.user.is_authenticated:
        is_super = request.user.is_superuser
        is_manager = request.user.groups.filter(name='Manager').exists()
        is_support = request.user.groups.filter(name='Support').exists()
        is_user = True

    return {
        'is_super': is_super,
        'is_manager': is_manager,
        'is_support': is_support,
        'is_user': is_user
    }

from django.contrib.auth.models import Group


MANAGER = "manager"
USER = "user"
ROLE_CHOICES = (MANAGER, USER)


def ensure_roles():
    for role in ROLE_CHOICES:
        Group.objects.get_or_create(name=role)


def bootstrap_roles(user_model):
    ensure_roles()

    manager_group = Group.objects.get(name=MANAGER)

    if not manager_group.user_set.exists() and user_model.objects.exists():
        first_user = user_model.objects.order_by("id").first()
        assign_role(first_user, MANAGER)

    user_group = Group.objects.get(name=USER)
    users_without_role = user_model.objects.exclude(groups__name__in=ROLE_CHOICES)

    for user in users_without_role:
        user.groups.add(user_group)


def assign_role(user, role):
    ensure_roles()

    if role not in ROLE_CHOICES:
        role = USER

    user.groups.remove(*Group.objects.filter(name__in=ROLE_CHOICES))
    user.groups.add(Group.objects.get(name=role))


def get_role(user):
    if not user.is_authenticated:
        return None

    if user.groups.filter(name=MANAGER).exists():
        return MANAGER

    if user.groups.filter(name=USER).exists():
        return USER

    return None


def is_manager(user):
    return get_role(user) == MANAGER

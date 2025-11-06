def permissions_wrapper(get_permissions, self):
    permissions = get_permissions(self)
    return [p() for p in permissions]

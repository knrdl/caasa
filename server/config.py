import os
from typing import Literal, get_args, Final, Set, Dict

AUTH_API_URL = os.getenv('AUTH_API_URL')
AUTH_API_FIELD_USERNAME = os.getenv('AUTH_API_FIELD_USERNAME', 'username')
AUTH_API_FIELD_PASSWORD = os.getenv('AUTH_API_FIELD_PASSWORD', 'password')
if not AUTH_API_URL:
    raise Exception('please provide AUTH_API_URL env var')

PermissionType = Literal[
    'info', 'info-annotations', 'state', 'logs', 'term', 'procs', 'files', 'files-read', 'files-write']
PERMISSIONS: Final[Set[PermissionType]] = set(get_args(PermissionType))

ROLES_PERMS: Dict[str, Set[PermissionType]] = {}
for key, value in os.environ.items():
    if key.startswith('ROLES_'):
        role_name = key.removeprefix('ROLES_').strip().replace('_', '.')
        if role_name:
            permissions = {p.strip() for p in value.split(',')}
            permissions = {p for p in permissions if p}
            unknown_permission = next((p for p in permissions if p not in PERMISSIONS), None)
            if unknown_permission:
                raise Exception(f'unknown permission "{unknown_permission}" for role "{role_name}"')
            ROLES_PERMS[role_name] = permissions

if not ROLES_PERMS:
    raise Exception('no roles defined, please set ROLES_* env vars')

print('Roles:')
for role in sorted(ROLES_PERMS):
    print('*', role, '->', ', '.join(sorted(ROLES_PERMS[role])))
print()

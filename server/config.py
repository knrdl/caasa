import os
from typing import Dict, Final, Literal, Set, get_args

from logger import logger

AUTH_API_URL = os.getenv('AUTH_API_URL')
AUTH_API_FIELD_USERNAME = os.getenv('AUTH_API_FIELD_USERNAME', 'username')
AUTH_API_FIELD_PASSWORD = os.getenv('AUTH_API_FIELD_PASSWORD', 'password')
WEBPROXY_AUTH_HEADER = os.getenv('WEBPROXY_AUTH_HEADER')
if not AUTH_API_URL and not WEBPROXY_AUTH_HEADER:
    raise Exception('No authentication method given. Please provide the environment variables.')
if AUTH_API_URL and WEBPROXY_AUTH_HEADER:
    raise Exception('WebForm authentication and WebProxy authentication cannot both be activated.')

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

logger.info('Roles -> Permissions:')
for role in sorted(ROLES_PERMS):
    logger.info('* ' + role + ' -> ' + ', '.join(sorted(ROLES_PERMS[role])))
logger.info('')

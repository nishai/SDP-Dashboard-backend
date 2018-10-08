import ldap
from django_auth_ldap.backend import LDAPBackend
from django_auth_ldap.config import LDAPSearch

# """
# Shared Settings
#   - LDAP: `v3`
#   - Search Subcontexts: `Yes`
#   - Distinguished Name: `DS\a1234… + Password`
#   - Data Mappings (remember to lock):
#     - Firstname: `givenName`
#     - Surname: `sn`
#     - Email: `mail`
#     - ID Number: `cn`
#   - Password change url:
#     - https://passwordreset.wits.ac.za/default.aspx
# """

# ========================================================================= #
# SETTINGS                                                                  #
# ========================================================================= #

# """
#  'distinguishedname': ['CN=1386161,OU=PGPROG,OU=FSCI,OU=Students,OU=Wits University,DC=ss,DC=WITS,DC=AC,DC=ZA'],
#  'memberof': ['CN=FSCI,OU=Faculty,OU=Groups,OU=Wits University,DC=ss,DC=WITS,DC=AC,DC=ZA'],
#  'objectcategory': ['CN=Person,CN=Schema,CN=Configuration,DC=RT,DC=WITS,DC=AC,DC=ZA'],
#  'objectclass': ['top', 'person', 'organizationalPerson', 'user'],
#  'employeeid': ['1386161'],
#  'name': ['1386161'],
#  'samaccountname': ['1386161'],
#  'uid': ['1386161'],
#  'cn': ['1386161'],
#  'displayname': ['1386161'],
#  'description': ['Program Status: ENROLLED, Modified on: 2018-08-24 00:00:00'],
#  """
_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email_human": "mail",
    "email": "userprincipalname",
    "id_number": "cn",
}

_ALWAYS_UPDATE_USER = True

_CONNTECTION_OPTIONS = {
    ldap.OPT_DEBUG_LEVEL: 0,
    ldap.OPT_REFERRALS: 0
}


# ========================================================================= #
# STUDENTS                                                                  #
# ========================================================================= #

# TODO: Extract common behavior
class LDAPBackendWitsStudents(LDAPBackend):

    settings_prefix = "AUTH_LDAP_SS_"

    default_settings = {
        'SERVER_URI': 'ldap://ss.wits.ac.za',
        'USER_SEARCH': LDAPSearch("ou=students,ou=wits university,dc=ss,dc=wits,dc=ac,dc=za", ldap.SCOPE_SUBTREE, "(cn=%(user)s)"),
        'CONNECTION_OPTIONS': _CONNTECTION_OPTIONS,
        'ALWAYS_UPDATE_USER': _ALWAYS_UPDATE_USER,
        'USER_ATTR_MAP': _USER_ATTR_MAP,
    }

    def authenticate_ldap_user(self, ldap_user, password):
        self.settings.BIND_DN = f'{ldap_user._username}@students.wits.ac.za'
        self.settings.BIND_PASSWORD = password
        try:
            username = super(LDAPBackendWitsStudents, self).authenticate_ldap_user(ldap_user, password)
            print(f" - Authenticated {ldap_user.attrs['employeetype'][0]}: {ldap_user._username} ({ldap_user.attrs['sn'][0]}, {ldap_user.attrs['givenName'][0]})")
        except:
            username = None
        return username


# ========================================================================= #
# STAFF                                                                     #
# ========================================================================= #

# TODO: Extract common behavior
class LDAPBackendWitsStaff(LDAPBackend):

    settings_prefix = "AUTH_LDAP_DS_"

    default_settings = {
        'SERVER_URI': 'ldap://ds.wits.ac.za',
        'USER_SEARCH': LDAPSearch("ou=wits university,dc=ds,dc=wits,dc=ac,dc=za", ldap.SCOPE_SUBTREE, "(cn=%(user)s)"),
        'CONNECTION_OPTIONS': _CONNTECTION_OPTIONS,
        'ALWAYS_UPDATE_USER': _ALWAYS_UPDATE_USER,
        'USER_ATTR_MAP': _USER_ATTR_MAP,
    }

    def authenticate_ldap_user(self, ldap_user, password):
        self.settings.BIND_DN = f'{ldap_user._username}@wits.ac.za'
        self.settings.BIND_PASSWORD = password
        try:
            username = super(LDAPBackendWitsStaff, self).authenticate_ldap_user(ldap_user, password)
            print(
                f" - Authenticated {ldap_user.attrs['employeetype'][0]}: {ldap_user._username} ({ldap_user.attrs['sn'][0]}, {ldap_user.attrs['givenName'][0]})")
        except:
            username = None
        return username

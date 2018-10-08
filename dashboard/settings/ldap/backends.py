from pprint import pprint

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
#  'employeetype': ['Student'],     # student only
#  'name': ['1386161'],
#  'samaccountname': ['1386161'],
#  'uid': ['1386161'],
#  'cn': ['1386161'],
#  'displayname': ['1386161'],
#  'description': ['Program Status: ENROLLED, Modified on: 2018-08-24 00:00:00'],
#  """

# """
#  'department': ['Mathematical Sciences'],
#  'description': ['Faculty Of Science - Mathematical Sciences'],
#  'distinguishedname': ['CN=A0056504,OU=Mathematical Sciences,OU=Faculty of Science,OU=Wits University,DC=ds,DC=WITS,DC=AC,DC=ZA'],
#  'legacyexchangedn': ['/o=WITS/ou=Exchange Administrative Group (FYDIBOHF23SPDLT)/cn=Recipients/cn=A00565049bc'],
#  'manager': ['CN=09400396,OU=Faculty of Science,OU=Wits University,DC=ds,DC=WITS,DC=AC,DC=ZA'],
#  'memberof': ['CN=_sec_pw_80days,OU=Groups,OU=Wits University,DC=ds,DC=WITS,DC=AC,DC=ZA',
#               'CN=_MSG_000083,OU=Mail Enabled Security Groups,OU=Groups,OU=Wits University,DC=ds,DC=WITS,DC=AC,DC=ZA',
#               'CN=_MSG_000499,OU=Mail Enabled Security Groups,OU=Groups,OU=Wits University,DC=ds,DC=WITS,DC=AC,DC=ZA',
#               'CN=_MSG_000413,OU=Mail Enabled Security Groups,OU=Groups,OU=Wits University,DC=ds,DC=WITS,DC=AC,DC=ZA'],
#  'msexchhomeservername': ['/o=WITS/ou=Exchange Administrative Group (FYDIBOHF23SPDLT)/cn=Configuration/cn=Servers/cn=EKHO'],
#  'objectcategory': ['CN=Person,CN=Schema,CN=Configuration,DC=RT,DC=WITS,DC=AC,DC=ZA'],
#  'objectclass': ['top', 'person', 'organizationalPerson', 'user'],
#  'title': ['Claim Paid'],
#  'displayname': ['Or Hanoch'],
#  'givenname': ['Or'],
#  'sn': ['Hanoch'],
#  'cn': ['A0056504'],
#  'name': ['A0056504'],
#  'employeeid': ['A0056504'],
#  'samaccountname': ['A0056504'],
#  'mailnickname': ['or.hanoch'],
#  'mail': ['or.hanoch@wits.ac.za'],
#  'userprincipalname': ['A0056504@wits.ac.za'],
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
        'USER_SEARCH': LDAPSearch("OU=Students,OU=Wits University,DC=ss,DC=WITS,DC=AC,DC=ZA", ldap.SCOPE_SUBTREE, "(cn=%(user)s)"),
        'CONNECTION_OPTIONS': _CONNTECTION_OPTIONS,
        'ALWAYS_UPDATE_USER': _ALWAYS_UPDATE_USER,
        'USER_ATTR_MAP': _USER_ATTR_MAP,
    }

    def authenticate_ldap_user(self, ldap_user, password):
        print(" - Attempting Authentication as Student")
        self.settings.BIND_DN = f'{ldap_user._username}@students.wits.ac.za'
        self.settings.BIND_PASSWORD = password
        try:
            username = super(LDAPBackendWitsStudents, self).authenticate_ldap_user(ldap_user, password)
        except:
            username = None
        if username:
            print(f" - Authenticated as Student: {ldap_user._username} ({ldap_user.attrs['sn'][0]}, {ldap_user.attrs['givenName'][0]})")
        return username


# ========================================================================= #
# STAFF                                                                     #
# ========================================================================= #

# TODO: Extract common behavior
class LDAPBackendWitsStaff(LDAPBackend):

    settings_prefix = "AUTH_LDAP_DS_"

    default_settings = {
        'SERVER_URI': 'ldap://ds.wits.ac.za',
        'USER_SEARCH': LDAPSearch("OU=Wits University,DC=ds,DC=WITS,DC=AC,DC=ZA", ldap.SCOPE_SUBTREE, "(cn=%(user)s)"),
        'CONNECTION_OPTIONS': _CONNTECTION_OPTIONS,
        'ALWAYS_UPDATE_USER': _ALWAYS_UPDATE_USER,
        'USER_ATTR_MAP': _USER_ATTR_MAP,
    }

    def authenticate_ldap_user(self, ldap_user, password):
        print(" - Attempting Authentication as Staff")
        self.settings.BIND_DN = f'{ldap_user._username}@wits.ac.za'
        self.settings.BIND_PASSWORD = password
        try:
            username = super(LDAPBackendWitsStaff, self).authenticate_ldap_user(ldap_user, password)
        except:
            username = None
        if username is not None:
            print(f" - Authenticated as Staff: {ldap_user._username} ({ldap_user.attrs['sn'][0]}, {ldap_user.attrs['givenName'][0]})")
        return username

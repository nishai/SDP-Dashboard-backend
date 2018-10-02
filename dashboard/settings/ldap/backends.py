import ldap
from django_auth_ldap.backend import LDAPBackend
from django_auth_ldap.config import LDAPSearch

"""
Shared Settings
  - LDAP: `v3`
  - Search Subcontexts: `Yes`
  - Distinguished Name: `DS\a1234… + Password`
  - Data Mappings (remember to lock):
    - Firstname: `givenName`
    - Surname: `sn`
    - Email: `mail`
    - ID Number: `cn`
"""


class LDAPBackendStudents(LDAPBackend):
    """
    SS (Students)
      - Host:
        - `ldap://ss.wits.ac.za`
        - `ldap://146.141.8.201`
      - Context:
        - `･       ou=students,ou=wits university,dc=ss,dc=wits,dc=ac,dc=za` # wits
        - `ou=FSCI,ou=students,ou=wits university,dc=ss,dc=wits,dc=ac,dc=za` # science
        - `ou=FEBE,ou=students,ou=wits university,dc=ss,dc=wits,dc=ac,dc=za` # engeneering
      - Password change url:
        - https://passwordreset.wits.ac.za/default.aspx
    """
    # ldap settings
    settings_prefix = "AUTH_LDAP_SS_"

    # global vars
    SERVER_URI = 'ldap://ss.wits.ac.za/:389'
    USER_SEARCH = LDAPSearch(
        'ou=students,ou=wits university,dc=ss,dc=wits,dc=ac,dc=za',
        ldap.SCOPE_SUBTREE,
        '(uid=students\\%(user)s)',
    )

class LDAPBackendStaff(LDAPBackend):
    """
    DS (Staff)
      - Host:
        - `ldap://ds.wits.ac.za`
        - `ldap://146.141.128.150`
      - Contexts:
        - `･                                                   ou=wits university,dc=ds,dc=wits,dc=ac,dc=za`
        - `･                             ou=faculty of science,ou=wits university,dc=ds,dc=wits,dc=ac,dc=za`
        - `ou=Faculty of Engineering and the Built Environment,ou=Wits University,dc=ds,dc=wits,dc=ac,dc=za`
        - `･         ou=Faculty of Commerce\, Law & Management,ou=Wits University,dc=ds,dc=wits,dc=ac,dc=za`
    """
    # ldap settings
    settings_prefix = "AUTH_LDAP_DS_"

    # global vars
    SERVER_URI = 'ldap://ds.wits.ac.za/:389'
    USER_SEARCH = LDAPSearch(
        'ou=wits university,dc=ds,dc=wits,dc=ac,dc=za',
        ldap.SCOPE_SUBTREE,
        '(uid=ds\\%(user)s)',  # TODO: Check https://www.wits.ac.za/library/about-us/services/wireless-access-setup/
    )

from django_auth_ldap.backend import LDAPBackend



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
  - Password change url:
    - https://passwordreset.wits.ac.za/default.aspx
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
        - `ou=FEBE,ou=students,ou=wits university,dc=ss,dc=wits,dc=ac,dc=za` # engineering
    """
    # ldap settings
    settings_prefix = "AUTH_LDAP_SS_"



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

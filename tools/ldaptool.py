#coding=utf-8

import sys,ldap
import ldap

LDAP_HOST = ''
USER = 'cn=admin,dc=xxx,dc=cn'
PASSWORD = 'xxxx'
BASE_DN = 'dc=xxxx,dc=cn'

class LDAPTool:
     
    def __init__(self,ldap_host=None,base_dn=None,user=None,password=None):
        if not ldap_host:
            ldap_host = LDAP_HOST
        if not base_dn:
            self.base_dn = BASE_DN
        if not user:
            user = USER
        if not password:
            password = PASSWORD
        try:
            self.ldapconn = ldap.initialize(ldap_host)
            self.ldapconn.protocal_version = ldap.VERSION3
            self.ldapconn.simple_bind(user,password)
        except ldap.LDAPError as e:
            print(e)

    def ldap_search_mail(self,email):
        obj = self.ldapconn
        obj.protocal_version = ldap.VERSION3
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        searchFilter = "mail=" + email
        try:
            ldap_result_id = obj.search(self.base_dn, searchScope, searchFilter, retrieveAttributes)
            result_type, result_data = obj.result(ldap_result_id, 0)
            if result_type == ldap.RES_SEARCH_ENTRY:
                #dn = result[0][0]
                return True
            else:
                return False
        except ldap.LDAPError as e:
            print(e)


    def ldap_search_dn(self,uid=None):
        obj = self.ldapconn
        obj.protocal_version = ldap.VERSION3
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None 
        searchFilter = "cn=" + uid
        
        try:
            ldap_result_id = obj.search(self.base_dn, searchScope, searchFilter, retrieveAttributes)
            result_type, result_data = obj.result(ldap_result_id, 0)
            #返回数据格式
            #('cn=django,ou=users,dc=huoqiu,dc=cn',
            #    {  'objectClass': ['inetOrgPerson', 'top'],
            #        'userPassword': ['{MD5}lueSGJZetyySpUndWjMBEg=='],
            #        'cn': ['django'], 'sn': ['django']  }  )
            #
            if result_type == ldap.RES_SEARCH_ENTRY:
                #dn = result[0][0]
                return result_data[0][0]
            else:
                return None
        except ldap.LDAPError as e:
            print(e)

    def ldap_get_user(self,uid=None):
        obj = self.ldapconn
        obj.protocal_version = ldap.VERSION3
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None 
        searchFilter = "cn=" + uid
        try:
            ldap_result_id = obj.search(self.base_dn, searchScope, searchFilter, retrieveAttributes)
            result_type, result_data = obj.result(ldap_result_id, 0)
            if result_type == ldap.RES_SEARCH_ENTRY:
                username = result_data[0][1]['cn'][0]
                email = result_data[0][1]['mail'][0]
                nick = result_data[0][1]['sn'][0]
                result = {'username':username,'email':email,'nick':nick}
                return result
            else:
                return None
        except ldap.LDAPError as e:
            print(e)
         
                 
    def  ldap_add(self):
        pass
    
    def ldap_get(self,uid=None,passwd=None):
        obj = self.ldapconn
        target_cn = self.ldap_search_dn(uid)    
        try:
            if obj.simple_bind_s(target_cn,passwd):
                return True
            else:
                return False
        except ldap.LDAPError as e:
            print(e)

    
    def ldap_update_pass(self,uid=None,oldpass=None,newpass=None):
        modify_entry = [(ldap.MOD_REPLACE,'userpassword',newpass)]
        obj = self.ldapconn
        target_cn = self.ldap_search_dn(uid)
        try:
            obj.simple_bind_s(target_cn,oldpass)
            obj.passwd_s(target_cn,oldpass,newpass)
            return True
        except ldap.LDAPError as e:
            return False

    def reset_user_pass(self,user,newpass):
        obj = self.ldapconn
        dn="cn=" + user + ",ou=users," + BASE_DN
        modify_list = [(ldap.MOD_REPLACE, 'userPassword', newpass.encode("utf-8"))]
        try:
            result = obj.modify_s(dn, modify_list)
        except ldap.LDAPError as e:
            return False, e
        else:
            if result[0] == 103:
                return True, []
            else:
                return False, result[1]

    
    def ldap_del(self):
        pass

if __name__ == '__main__':
    ladp=LDAPTool()
    a = ladp.ldap_search_mail('')
    print a
    #result = ladp.reset_user_pass('lixing','123456')
    #print result
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# Copyright Commvault Systems, Inc.
# See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Main file for managing users on this commcell

Users and User are only the two classes defined in this commcell

Users
    __init__()                          --  initializes the users class object

    __str__()                           --  returns all the users associated with the
                                            commcell

    __repr__()                          --  returns the string for the instance of the
                                            Users class

    _get_users()                        --  gets all the users on this commcell

    _process_add_or_delete_response()   --  process the add or delete users response

    add()                               --  adds local/external user to commcell

    has_user()                          --  checks if user with specified user exists
                                            on this commcell

    get()                               --  returns the user class object for the
                                            specified user name

    delete()                            --  deletes the user on this commcell

    refresh()                           --  refreshes the list of users on this
                                            commcell

    all_users()                         --  Returns all the users present in the commcell

User
    __init__()                          --  initiaizes the user class object

    __repr__()                          --  returns the string for the instance of the
                                            User class

    _get_user_id()                      --  returns the user id associated with this
                                            user

    _get_user_properties()              --  gets all the properties associated with
                                            this user

    _update_user_props()                --  updates the properties associated with
                                            this user

    _update_usergroup_request()         --  makes the request to update usergroups
                                            associated with this user

    user_name()                         --  returns the name of this user

    user_id()                           --  returns the id of this user

    description()                       --  returns the description of this user

    email()                             --  returns the email of this user

    associated_usergroups()             --  returns the usergroups associated with
                                            this user

    add_usergroups()                    --  associates the usergroups with this user

    remove_usergroups()                 --  disassociated the usergroups with this user

    overwrite_usergroups()              --  reassociates the usergroups with this user

    refresh()                           --  refreshes the properties of this user

    update_security_associations        --  updates 3-way security associations on user

"""

from base64 import b64encode
from past.builtins import basestring
from .security_association import SecurityAssociation
from ..exception import SDKException



class Users(object):
    """Class for maintaining all the configured users on this commcell"""

    def __init__(self, commcell_object):
        """Initializes the users class object for this commcell

            Args:
                commcell_object (object)  --  instance of the Commcell class

            Returns:
                object - instance of the Clients class
        """
        self._commcell_object = commcell_object
        self._users = self._get_users()

    def __str__(self):
        """Representation string consisting of all users of the commcell.

            Returns:
                str - string of all the users configured on the commcell
        """
        representation_string = '{:^5}\t{:^20}\n\n'.format('S. No.', 'Users')

        for index, user in enumerate(self._users):
            sub_str = '{:^5}\t{:20}\n'.format(index + 1, user)
            representation_string += sub_str

        return representation_string.strip()

    def __repr__(self):
        """Representation string for the instance of the Users class."""
        return "Users class instance for Commcell: '{0}'".format(
            self._commcell_object.commserv_name
        )

    def _get_users(self):
        """Returns the list of users configured on this commcell

            Returns:
                dict of all the users on this commcell
                    {
                        'user_name_1': user_id_1
                    }

        """
        get_all_user_service = self._commcell_object._services['USERS']

        flag, response = self._commcell_object._cvpysdk_object.make_request(
            'GET', get_all_user_service
        )

        if flag:
            if response.json() and 'users' in response.json():
                users_dict = {}

                for user in response.json()['users']:
                    temp_name = user['userEntity']['userName'].lower()
                    temp_id = user['userEntity']['userId']
                    users_dict[temp_name] = temp_id

                return users_dict
            else:
                raise SDKException('Response', '102')
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)

    def _process_add_or_delete_response(self, flag, response):
        """Processes the flag and response received from the server during add delete request

            Args:
                request_object  (object)  --  request objects specifying the details
                                              to request

            Raises:
                SDKException:
                    if response is empty

                    if reponse is not success
        """
        if flag:
            if response.json():
                error_code = -1
                error_message = ''
                if 'response' in response.json():
                    response_json = response.json()['response'][0]
                    error_code = response_json['errorCode']

                elif 'errorCode' in response.json():
                    error_code = response.json()['errorCode']
                    if 'errorMessage' in response:
                        error_message = response['errorMessage']

                return error_code, error_message

            else:
                raise SDKException('Response', '102')
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)

    def _add_user(self, create_user_request):
        """Makes the add user request on the server

            Args:
                create_user_request     (dict)  --  request json to create an user

            Raises:
                SDKException:
                    if failed to add user
        """
        add_user = self._commcell_object._services['USERS']

        flag, response = self._commcell_object._cvpysdk_object.make_request(
            'POST', add_user, create_user_request
        )
        error_code, error_message = self._process_add_or_delete_response(flag, response)

        if not error_message:
            error_message = 'Failed to add user. Please check logs for further details.'

        if error_code != 0:
            raise SDKException('User', '102', error_message)

        self._users = self._get_users()

    def add(self,
            user_name,
            full_name,
            email,
            domain=None,
            password=None,
            system_generated_password=False,
            local_usergroups=None,
            entity_dictionary=None):
        """Adds a local/external user to this commcell

            Args:
                user_name                     (str)     --  name of the user to be
                                                            created

                full_name                     (str)     --  full name of the user to be
                                                            created

                email                         (str)     --  email of the user to be
                                                            created

                domain                        (str)     --  Needed in case you are adding
                                                            external user

                password                      (str)     --  password of the user to be
                                                            created
                    default: None

                local_usergroups              (str)     --  user can be member of
                                                            these user groups

                system_generated_password     (bool)    --  if set to true system
                                                            defined password will be used
                    default: False

                entity_dictionary   --      combination of entity_type, entity names
                                            and role

                e.g.: security_dict={
                                'assoc1':
                                    {
                                        'entity_type':['entity_name'],
                                        'entity_type':['entity_name', 'entity_name'],
                                        'role': ['role1']
                                    },
                                'assoc2':
                                    {
                                        'mediaAgentName': ['networktestcs', 'standbycs'],
                                        'clientName': ['Linux1'],
                                        'role': ['New1']
                                        }
                                    }
                entity_type         --      key for the entity present in dictionary
                                            on which user will have access

                entity_name         --      Value of the key

                 role               --      key for role name you specify

                e.g.: {"clientName":"Linux1"}
                entity_type:    clientName, mediaAgentName, libraryName, userName,
                                userGroupName, storagePolicyName, clientGroupName,
                                schedulePolicyName, locationName, providerDomainName,
                                alertName, workflowName, policyName, roleName

                entity_name:    client name for entity_type 'clientName'
                                Media agent name for entitytype 'mediaAgentName'
                                similar for other entity_typees

            Raises:
                SDKException:
                    if data type of input is invalid

                    if user with specified name already exists

                    if password or system_generated_password are not set

                    if failed to add user to commcell
        """
        if domain:
            username = "{0}\\{1}".format(domain, user_name)
            password = ""
            system_generated_password = False
        else:
            username = user_name
            if not password and not system_generated_password:
                raise SDKException(
                    'User',
                    '102',
                    'Both password and system_generated_password are not set.'
                    'Please specify password or mark system_generated_password as true')

        if not (isinstance(username, basestring) and
                isinstance(email, basestring)):
            raise SDKException('User', '101')

        if self.has_user(username):
            raise SDKException(
                'User', '102', "User {0} already exists on this commcell.".format(
                    username)
            )

        if password is not None:
            password = b64encode(password.encode()).decode()
        else:
            password = ''

        if local_usergroups:
            groups_json = [{"userGroupName": lname} for lname in local_usergroups]
        else:
            groups_json = [{}]

        security_json = {}
        if entity_dictionary:
            security_request = SecurityAssociation._security_association_json(
                entity_dictionary=entity_dictionary)
            security_json = {
                "associationsOperationType": "ADD",
                "associations": security_request
                }

        create_user_request = {
            "users": [{
                "password": password,
                "email": email,
                "fullName": full_name,
                "systemGeneratePassword": system_generated_password,
                "userEntity": {
                    "userName": username
                },
                "securityAssociations": security_json,
                "associatedUserGroups": groups_json
            }]
        }
        self._add_user(create_user_request)
        return self.get(username)

    def has_user(self, user_name):
        """Checks if any user with specified name exists on this commcell

            Args:
                user_name         (str)     --     name of the user which has to be
                                                   checked if exists

            Raises:
                SDKException:
                    if data type of input is invalid
        """
        if not isinstance(user_name, basestring):
            raise SDKException('User', '101')

        return self._users and user_name.lower() in self._users

    def get(self, user_name):
        """Returns the user object for the specified user name

            Args:
                user_name  (str)  --  name of the user for which the object has to be
                                      created

            Raises:
                SDKException:
                    if user doesn't exist with specified name
        """
        if not self.has_user(user_name):
            raise SDKException(
                'User', '102', "User {0} doesn't exists on this commcell.".format(
                    user_name)
            )

        return User(self._commcell_object, user_name, self._users[user_name.lower()])

    def delete(self, user_name, new_user=None, new_usergroup=None):
        """Deletes the specified user from the existing commcell users

            Args:
                user_name       (str)   --  name of the user which has to be deleted

                new_user        (str)   --  name of the target user, whom the ownership
                                            of entities should be transferred

                new_usergroup   (str)   --  name of the user group, whom the ownership
                                            of entities should be transferred

                Note: either user or usergroup  should be provided for ownership
                transfer not both.

            Raises:
                SDKException:
                    if user doesn't exist

                    if new user and new usergroup any of these is passed and these doesn't
                    exist on commcell

                    if both user and usergroup is passed for ownership transfer

                    if both user and usergroup is not passed for ownership transfer

                    if response is not success

        """
        if not self.has_user(user_name):
            raise SDKException(
                'User', '102', "User {0} doesn't exists on this commcell.".format(
                    user_name)
            )
        if new_user and new_usergroup:
            raise SDKException(
                'User', '102', "{0} and {1} both can not be set as owner!! "
                "please send either new_user or new_usergroup".format(new_user, new_usergroup)
            )
        else:
            if new_user:
                if not self.has_user(new_user):
                    raise SDKException(
                        'User', '102', "User {0} doesn't exists on this commcell.".format(
                            new_user)
                    )
                new_user_id = self._users[new_user.lower()]
                new_group_id = 0
            else:
                if new_usergroup:
                    if not self._commcell_object.user_groups.has_user_group(new_usergroup):
                        raise SDKException(
                            'UserGroup', '102', "UserGroup {0} doesn't exists "
                            "on this commcell.".format(new_usergroup)
                        )
                else:
                    raise SDKException(
                        'User', '102',
                        "Ownership transfer is mondatory!! Please provide new owner information"
                    )
                new_group_id = self._commcell_object.user_groups.get(new_usergroup).user_group_id
                new_user_id = 0

        delete_user = self._commcell_object._services['DELETE_USER'] %(
            self._users[user_name.lower()], new_user_id, new_group_id)
        flag, response = self._commcell_object._cvpysdk_object.make_request(
            'DELETE', delete_user
        )
        error_code, error_message = self._process_add_or_delete_response(flag, response)
        if not error_message:
            error_message = 'Failed to delete user. Please check logs for further details.'
        if error_code != 0:
            raise SDKException('User', '102', error_message)
        self._users = self._get_users()

    def refresh(self):
        """Refresh the list of Users on this commcell."""
        self._users = self._get_users()

    @property
    def all_users(self):
        """Returns the dict of all the users on the commcell

        dict of all the users on commcell
                   {
                      'user_name_1': user_id_1
                   }
        """
        return self._users


class User(object):
    """Class for representing a particular user configured on this commcell"""

    def __init__(self, commcell_object, user_name, user_id=None):
        """Initialize the User class object for specified user

            Args:
                commcell_object (object)  --  instance of the Commcell class

                user_name         (str)     --  name of the user

                user_id           (str)     --  id of the user
                    default: None

        """
        self._commcell_object = commcell_object
        self._user_name = user_name.lower()

        if user_id is None:
            self._user_id = self._get_user_id(self._user_name)
        else:
            self._user_id = user_id

        self._user = self._commcell_object._services['USER'] % (self._user_id)
        self._user_status = None
        self._email = None
        self._description = None
        self._associated_usergroups = None
        self._properties = None
        self._get_user_properties()

    def __repr__(self):
        """String representation of the instance of this class."""
        representation_string = 'User class instance for User: "{0}"'
        return representation_string.format(self.user_name)

    def _get_user_id(self, user_name):
        """Gets the user id associated with this user

            Args:
                user_name         (str)     --     name of the user whose

            Returns:
                int     -     id associated to the specified user
        """
        users = Users(self._commcell_object)
        return users.get(user_name).user_id

    def _get_user_properties(self):
        """Gets the properties of this user"""
        flag, response = self._commcell_object._cvpysdk_object.make_request(
            'GET', self._user
        )

        if flag:
            if response.json() and 'users' in response.json():
                self._properties = response.json()['users'][0]

                if 'enableUser' in self._properties:
                    self._user_status = self._properties['enableUser']

                if 'email' in self._properties:
                    self._email = self._properties['email']

                if 'description' in self._properties:
                    self._description = self._properties['description']

                if 'associatedUserGroups' in self._properties:
                    self._associated_usergroups = self._properties['associatedUserGroups']
            else:
                raise SDKException('Response', '102')
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)

    def _update_user_props(self, properties_dict):
        """Updates the properties of this user

            Args:
                properties_dict (dict)  --  user property dict which is to be updated
                    e.g.: {
                            "description": "My description"
                        }
            Returns:
                User Properties update dict
        """
        request_json = {
            "users": [{
                "userEntity": {
                    "userName": self.user_name
                }
            }]
        }

        request_json['users'][0].update(properties_dict)

        flag, response = self._commcell_object._cvpysdk_object.make_request(
            'POST', self._user, request_json
        )

        if flag:
            if response.json():
                if 'response' in response.json():
                    response_json = response.json()['response'][0]
                    error_code = response_json['errorCode']
                    error_message = response_json['errorString']
                    if not error_code == 0:
                        raise SDKException('Response', '101', error_message)
            else:
                raise SDKException('Response', '102')
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)

    def _update_usergroup_request(self, request_type, usergroups_list=None):
        """Updates the usergroups this user is associated to

            Args:
                usergroups_list     (list)     --     list of usergroups to be updated

                request_type         (str)     --     type of request to be done

            Raises:
                SDKException:

                    if failed to update usergroups

                    if usergroup is not list

                    if usergroup doesn't exixt on this commcell

        """
        update_usergroup_request = {
            "NONE": 0,
            "OVERWRITE": 1,
            "UPDATE": 2,
            "DELETE": 3,
        }

        if not isinstance(usergroups_list, list):
            raise SDKException('USER', '101')

        for usergroup in usergroups_list:
            if not self._commcell_object.user_groups.has_user_group(usergroup):
                raise SDKException(
                    'UserGroup', '102', "UserGroup {0} doesn't "
                    "exists on this commcell".format(usergroup)
                )

        associated_usergroups = []
        if usergroups_list:
            for usergroup in usergroups_list:
                temp = {
                    "userGroupName": usergroup
                }
                associated_usergroups.append(temp)

        update_usergroup_dict = {
            "associatedUserGroupsOperationType": update_usergroup_request[
                request_type.upper()],
            "associatedUserGroups": associated_usergroups
        }

        self._update_user_props(update_usergroup_dict)

    @property
    def user_name(self):
        """Returns the user name of this commcell user"""
        return self._user_name

    @property
    def user_id(self):
        """Returns the user id of this commcell user"""
        return self._user_id

    @property
    def description(self):
        """Returns the description associated with this commcell user"""
        return self._description

    @property
    def email(self):
        """Returns the email associated with this commcell user"""
        return self._email

    @description.setter
    def description(self, value):
        """Sets the description for this commcell user"""
        props_dict = {
            "description": value
        }
        self._update_user_props(props_dict)

    @property
    def associated_usergroups(self):
        """Returns the list of associated usergroups"""
        usergroups = []
        if self._associated_usergroups is not None:
            for usergroup in self._associated_usergroups:
                usergroups.append(usergroup['userGroupName'])
        return usergroups

    @property
    def status(self):
        """Returns the status of this commcell user"""
        return self._user_status

    @status.setter
    def status(self, value):
        """Sets the status for this commcell user"""
        request_json = {
            "users":[{
                "enableUser": value
            }]
        }
        usergroup_request = self._commcell_object._services['USER']%(self._user_id)
        flag, response = self._commcell_object._cvpysdk_object.make_request(
            'POST', usergroup_request, request_json
        )
        if flag:
            if response.json():
                if 'response' in response.json():
                    response_json = response.json()['response'][0]
                    error_code = response_json['errorCode']
                    error_message = response_json['errorString']
                    if not error_code == 0:
                        raise SDKException('Response', '101', error_message)
            else:
                raise SDKException('Response', '102')
        else:
            response_string = self._commcell_object._update_response_(response.text)
            raise SDKException('Response', '101', response_string)

    def add_usergroups(self, usergroups_list):
        """UPDATE the specified usergroups to this commcell user

            Args:
                usergroups_list     (list)  --     list of usergroups to be added
        """
        self._update_usergroup_request('UPDATE', usergroups_list)


    def remove_usergroups(self, usergroups_list):
        """DELETE the specified usergroups to this commcell user

            Args:
                usergroups_list     (list)  --     list of usergroups to be deleted
        """
        self._update_usergroup_request('DELETE', usergroups_list)

    def overwrite_usergroups(self, usergroups_list):
        """OVERWRITE the specified usergroups to this commcell user

            Args:
                usergroups_list     (list)  --     list of usergroups to be overwritten

        """
        self._update_usergroup_request('OVERWRITE', usergroups_list)

    def refresh(self):
        """Refresh the properties of the User."""
        self._get_user_properties()

    def update_security_associations(self, entity_dictionary, request_type):
        """handles three way associations (role-user-entities)

            Args:
                entity_dictionary   --      combination of entity_type, entity names
                                            and role
                e.g.: security_dict={
                                'assoc1':
                                    {
                                        'entity_type':['entity_name'],
                                        'entity_type':['entity_name', 'entity_name'],
                                        'role': ['role1']
                                    },
                                'assoc2':
                                    {
                                        'mediaAgentName': ['networktestcs', 'standbycs'],
                                        'clientName': ['Linux1'],
                                        'role': ['New1']
                                        }
                                    }

                entity_type         --      key for the entity present in dictionary
                                            on which user will have access

                entity_name         --      Value of the key

                role                --      key for role name you specify

                e.g.: {"clientName":"Linux1"}

                Entity Types are:   clientName, mediaAgentName, libraryName, userName,
                                    userGroupName, storagePolicyName, clientGroupName,
                                    schedulePolicyName, locationName, providerDomainName,
                                    alertName, workflowName, policyName, roleName

                entity_name:        client name for entity_type 'clientName'
                                    Media agent name for entitytype 'mediaAgentName'
                                    similar for other entity_types

                request_type        --      decides whether to ADD, DELETE or
                                            OVERWRITE user security association.

            Raises:
                SDKException:

                    if response is not success
        """
        update_user_request = {
            "NONE": 0,
            "OVERWRITE": 1,
            "UPDATE": 2,
            "DELETE": 3,
        }

        sec_request = {}
        if entity_dictionary:
            sec_request = SecurityAssociation._security_association_json(
                entity_dictionary=entity_dictionary)

        request_json = {
            "securityAssociations":{
                "associationsOperationType":update_user_request[request_type.upper()],
                "associations":sec_request
                }
        }
        self._update_user_props(request_json)

# digital_pass_updater.py
#
# Copyright 2022-2023 Pablo Sánchez Rodríguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import http.client


class PassKitWebService:

    @staticmethod
    def get_latest_version(web_service_url, pass_type_identifier,
                           serial_number, authentication_token):

        endpoint = '{}/v1/passes/{}/{}'.format(web_service_url,
                                               pass_type_identifier,
                                               serial_number)

        authorization = 'ApplePass {}'.format(authentication_token)
        headers = {'Authorization' : authorization}

        protocol, host_and_path = endpoint.split('//', 1)
        host, path = host_and_path.split('/', 1)

        connection = http.client.HTTPSConnection(host)
        connection.request("GET", '/{}'.format(path), headers=headers)

        return connection

    @staticmethod
    def get_from_new_location(new_location):
        print(new_location)
        protocol, host_and_path = new_location.split('//', 1)
        host, path = host_and_path.split('/', 1)

        connection = http.client.HTTPSConnection(host)
        connection.request("GET", '/{}'.format(path))

        return connection

class PassUpdater:

    @classmethod
    def update(this_class, a_pass):
        """ Download and return the latest version of a digital pass """

        if not a_pass.is_updatable() or a_pass.format() != 'pkpass':
            raise PassNotUpdatable()

        return this_class._update_pkpass(a_pass.adaptee())

    @classmethod
    def _update_pkpass(this_class, pkpass):
        """ Download and return the latest version of a PKPass """

        web_service_url = pkpass.web_service_url()
        pass_type_identifier = pkpass.pass_type_identifier()
        serial_number = pkpass.serial_number()
        authentication_token = pkpass.authentication_token()

        first_iteration = True
        last_response_status = -1
        new_location = None

        while first_iteration or last_response_status in [301, 302]:
            first_iteration = False

            if new_location:
                connection = PassKitWebService\
                                .get_from_new_location(new_location)
            else:
                connection = PassKitWebService\
                                .get_latest_version(web_service_url,
                                                    pass_type_identifier,
                                                    serial_number,
                                                    authentication_token)

            response = connection.getresponse()
            last_response_status = response.status

            if response.status == 200:
                """ 200 OK """
                pkpass_data = response.read()
                connection.close()
                return pkpass_data

            elif response.status in [204, 304]:
                """ 204 No Content / 304 Not Modified """
                connection.close()
                raise PassAlreadyUpdated()

            elif response.status in [301, 302]:
                """ 301 Moved Permanently / 302 Found """
                # Web Service URL has been updated
                new_location = response.getheader('Location')
                connection.close()
                continue

            raise PassUpdateError(response.status, response.reason)


class PassAlreadyUpdated(Exception):
    def __init__(self):
        message = _('Pass already updated')
        super().__init__(message)


class PassNotUpdatable(Exception):
    def __init__(self):
        message = _('Pass not updatable')
        super().__init__(message)


class PassUpdateError(Exception):
    def __init__(self, error_code, reason):
        message = _('Pass update error: {} {}').format(error_code, reason)
        super().__init__(message)

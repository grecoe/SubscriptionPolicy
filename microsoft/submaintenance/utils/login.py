import os
from .cmdline import CmdUtils
from .config import Configuration

class AzLoginUtils:
    @staticmethod
    def validate_login(credentials_json: str = None):
        """
        Validates the login. Steps taken
            - Check login status
            - Check use principal
                - True
                    If logged in as SP, do nothing more
                    If logged in NOT as SP, logout and login SP
                    If not logged in, just log in SP
                - False
                    If logged in, do nothing more
                    If not, raise an exception

        Credentials file must be a JSON file with the following required fields
        {
            "usePrincipal" : [true, false],
            "application" : "APP_ID",
            "credential" : "PASSWORD",
            "tenent" : "APP_TENENT"
        }
        """
        creds = None

        if credentials_json:
            if not os.path.exists(credentials_json):
                raise Exception("Credentials file invalid", credentials_json)
            else:
                creds = Configuration(credentials_json)

        current_login = AzLoginUtils.get_current_account()

        if creds and creds.usePrincipal:
            if current_login and current_login["user"]["name"] == creds.application:
                print("Already logged in with SP")
            else:
                print("Log in Service Principal")
                if current_login:
                    print("Logging out", current_login["user"]["name"])
                    AzLoginUtils.logout()
                
                AzLoginUtils.login_principal(creds)
                current_login = AzLoginUtils.get_current_account()

                if not current_login:
                    raise Exception("Invalid User Principal")
                
        elif not current_login:
            raise Exception("You must be logged in or have identified a service principal")

        print("Acting as -", current_login["user"]["name"])

    @staticmethod
    def get_current_account():
        command = "az account show"
        result = CmdUtils.get_command_output(command.split(" "))

        if isinstance(result, dict):
            return result
        
        return None

    @staticmethod
    def logout():
        command = "az logout"
        CmdUtils.get_command_output(command.split(" "))

    @staticmethod
    def login_principal(creds):
        command = "az login --service-principal --username {} --password {} --tenant {}".format(
            creds.application,
            creds.credential,
            creds.tenent
        )
        CmdUtils.get_command_output(command.split(" "))

import configparser

DEFAULT_APP_NAME = "my_app"
DEFAULT_CHECK_INTERVAL_SECONDS = 1
DEFAULT_TOKEN_FILE = "/var/run/vmnotification/token_file"
DEFAULT_TOKEN_FILE_CREATE = True
DEFAULT_TOKEN_OBFUSCATE_LOGFILE = False
DEFAULT_SERVICE_LOGFILE = "/var/log/vmnotification/vmnotification.log"
DEFAULT_SERVICE_LOG_LEVEL = "DEBUG"
DEFAULT_SERVICE_CONSOLE_LEVEL = "WARNING"
DEFAULT_SERVICE_LOGFILE_MAXSIZE_BYTES = 20 * 1024 * 1024
DEFAULT_SERVICE_LOGFILE_COUNT = 10
DEFAULT_VMOTION_LOGFILE = "/var/log/vmnotification/vmotion.log"
DEFAULT_VMOTION_LOGFILE_MAXSIZE_BYTES = 20 * 1024 * 1024
DEFAULT_VMOTION_LOGFILE_COUNT = 3


class VMNotificationConfig(object):

    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

        #
        # Default Section
        #
        self.app_name = self.config.get(section="DEFAULT",
                                        option="app_name",
                                        fallback=DEFAULT_APP_NAME)

        self.check_interval_seconds = self.config.getint(section="DEFAULT",
                                                         option="check_interval_seconds",
                                                         fallback=DEFAULT_CHECK_INTERVAL_SECONDS)

        self.pre_vmotion_cmd = self.config.get(section="DEFAULT",
                                               option="pre_vmotion_cmd")

        self.post_vmotion_cmd = self.config.get(section="DEFAULT",
                                                option="post_vmotion_cmd")

        #
        # Token Section
        #
        self.token_file = self.config.get(section="Token",
                                          option="token_file",
                                          fallback=DEFAULT_TOKEN_FILE)

        self.token_file_create = self.config.getboolean(section="Token",
                                                        option="token_file_create",
                                                        fallback=DEFAULT_TOKEN_FILE_CREATE)

        self.token_obfuscate_logfile = self.config.getboolean(section="Token",
                                                              option="token_obfuscate_logfile",
                                                              fallback=DEFAULT_TOKEN_OBFUSCATE_LOGFILE)

        #
        # Logging Section
        #
        self.service_logfile = self.config.get(section="Logging",
                                               option="service_logfile",
                                               fallback=DEFAULT_SERVICE_LOGFILE)

        self.service_logfile_level = self.config.get(section="Logging",
                                                     option="service_logfile_level",
                                                     fallback=DEFAULT_SERVICE_LOG_LEVEL)

        self.service_console_level = self.config.get(section="Logging",
                                                     option="service_console_level",
                                                     fallback=DEFAULT_SERVICE_CONSOLE_LEVEL)

        self.service_logfile_maxsize_bytes = self.config.getint(section="Logging",
                                                                option="service_logfile_maxsize_bytes",
                                                                fallback=DEFAULT_SERVICE_LOGFILE_MAXSIZE_BYTES)

        self.service_logfile_count = self.config.getint(section="Logging",
                                                        option="service_logfile_count",
                                                        fallback=DEFAULT_SERVICE_LOGFILE_COUNT)

        self.vmotion_logfile = self.config.get(section="Logging",
                                               option="vmotion_logfile",
                                               fallback=DEFAULT_VMOTION_LOGFILE)

        self.vmotion_logfile_maxsize_bytes = self.config.getint(section="Logging",
                                                                option="vmotion_logfile_maxsize_bytes",
                                                                fallback=DEFAULT_VMOTION_LOGFILE_MAXSIZE_BYTES)

        self.vmotion_logfile_count = self.config.getint(section="Logging",
                                                        option="vmotion_logfile_count",
                                                        fallback=DEFAULT_VMOTION_LOGFILE_COUNT)

    def json(self):
        return {
            "config_file": self.config_file,
            "app_name": self.app_name,
            "check_interval_seconds": self.check_interval_seconds,
            "pre_vmotion_cmd": self.pre_vmotion_cmd,
            "post_vmotion_cmd": self.post_vmotion_cmd,
            "token_file": self.token_file,
            "token_file_create": self.token_file_create,
            "token_obfuscate_logfile": self.token_obfuscate_logfile,
            "service_logfile": self.service_logfile,
            "service_logfile_level": self.service_logfile_level,
            "service_console_level": self.service_console_level,
            "service_logfile_maxsize_bytes": self.service_logfile_maxsize_bytes,
            "service_logfile_count": self.service_logfile_count,
            "vmotion_logfile": self.vmotion_logfile,
            "vmotion_logfile_maxsize_bytes": self.vmotion_logfile_maxsize_bytes,
            "vmotion_logfile_count": self.vmotion_logfile_count,
        }

    def print(self):
        for k, v in self.json().items():
            print(f"{ k }: '{ v }'")

    @property
    def app_name(self) -> str:
        return self._app_name

    @app_name.setter
    def app_name(self, app_name: str):
        if not isinstance(app_name, str) and len(app_name) < 1:
            raise ValueError(f"app_file must be a string with at least 1 character (input: '{app_name}')")
        self._app_name = app_name

    @property
    def check_interval_seconds(self) -> int:
        return self._check_interval_seconds

    @check_interval_seconds.setter
    def check_interval_seconds(self, check_interval_seconds: int):
        if not isinstance(check_interval_seconds, int):
            raise ValueError(f"check_interval_seconds must be an integer (input: '{check_interval_seconds}')")
        if check_interval_seconds < 1:
            raise ValueError(f"check_interval_seconds must be greater than 0 (input: {check_interval_seconds})")
        self._check_interval_seconds = check_interval_seconds

    @property
    def pre_vmotion_cmd(self) -> str:
        return self._pre_vmotion_cmd

    @pre_vmotion_cmd.setter
    def pre_vmotion_cmd(self, pre_vmotion_cmd: str):
        if not isinstance(pre_vmotion_cmd, str):
            raise ValueError(f"pre_vmotion_cmd must be a string (input: '{pre_vmotion_cmd}')")
        self._pre_vmotion_cmd = pre_vmotion_cmd

    @property
    def post_vmotion_cmd(self) -> str:
        return self._post_vmotion_cmd

    @post_vmotion_cmd.setter
    def post_vmotion_cmd(self, post_vmotion_cmd: str):
        if not isinstance(post_vmotion_cmd, str):
            raise ValueError(f"post_vmotion_cmd must be a string (input: '{post_vmotion_cmd}')")
        self._post_vmotion_cmd = post_vmotion_cmd

    @property
    def token_file(self) -> str:
        return self._token_file

    @token_file.setter
    def token_file(self, token_file: str):
        if not isinstance(token_file, str) and len(token_file) < 1:
            raise ValueError(f"token_file must be a string with at least 1 character (input: '{token_file}')")
        self._token_file = token_file

    @property
    def token_file_create(self) -> bool:
        return self._token_file_create

    @token_file_create.setter
    def token_file_create(self, token_file_create: str):
        if not isinstance(token_file_create, bool):
            raise ValueError(f"token_file_create must be a boolean (input: '{token_file_create}')")
        self._token_file_create = token_file_create

    @property
    def token_obfuscate_logfile(self) -> bool:
        return self._token_obfuscate_logfile

    @token_obfuscate_logfile.setter
    def token_obfuscate_logfile(self, token_obfuscate_logfile: str):
        if not isinstance(token_obfuscate_logfile, bool):
            raise ValueError(f"token_obfuscate_logfile must be a boolean (input: '{token_obfuscate_logfile}')")
        self._token_obfuscate_logfile = token_obfuscate_logfile

    @property
    def service_logfile(self) -> str:
        return self._service_logfile

    @service_logfile.setter
    def service_logfile(self, service_logfile: str):
        if not isinstance(service_logfile, str) and len(service_logfile) < 1:
            raise ValueError(f"service_logfile must be a string with at least 1 character (input: '{service_logfile}')")
        self._service_logfile = service_logfile

    @property
    def service_logfile_level(self) -> str:
        return self._service_logfile_level

    @service_logfile_level.setter
    def service_logfile_level(self, service_logfile_level: str):
        if not isinstance(service_logfile_level, str):
            raise ValueError(f"service_logfile_level must be a string (input: '{service_logfile_level}')")
        self._service_logfile_level = service_logfile_level

    @property
    def service_console_level(self) -> str:
        return self._service_console_level

    @service_console_level.setter
    def service_console_level(self, service_console_level: str):
        if not isinstance(service_console_level, str):
            raise ValueError(f"service_console_level must be a string (input: '{service_console_level}')")
        self._service_console_level = service_console_level

    @property
    def service_logfile_maxsize_bytes(self) -> int:
        return self._service_logfile_maxsize_bytes

    @service_logfile_maxsize_bytes.setter
    def service_logfile_maxsize_bytes(self, service_logfile_maxsize_bytes: int):
        if service_logfile_maxsize_bytes < 1:
            raise ValueError(
                f"service_logfile_maxsize_bytes must be greater than 1024 (was {service_logfile_maxsize_bytes}).")
        self._service_logfile_maxsize_bytes = service_logfile_maxsize_bytes

    @property
    def service_logfile_count(self) -> int:
        return self._service_logfile_count

    @service_logfile_count.setter
    def service_logfile_count(self, service_logfile_count: int):
        if service_logfile_count < 2:
            raise ValueError(f"service_logfile_count must be greater than 1 (was {service_logfile_count}).")
        self._service_logfile_count = service_logfile_count

    @property
    def vmotion_logfile(self) -> str:
        return self._vmotion_logfile

    @vmotion_logfile.setter
    def vmotion_logfile(self, vmotion_logfile: str):
        if not isinstance(vmotion_logfile, str) and len(vmotion_logfile) < 1:
            raise ValueError(f"service_logfile must be a string with at least 1 character (input: '{vmotion_logfile}')")
        self._vmotion_logfile = vmotion_logfile

    @property
    def vmotion_logfile_maxsize_bytes(self) -> int:
        return self._vmotion_logfile_maxsize_bytes

    @vmotion_logfile_maxsize_bytes.setter
    def vmotion_logfile_maxsize_bytes(self, vmotion_logfile_maxsize_bytes: int):
        if vmotion_logfile_maxsize_bytes < 1:
            raise ValueError(
                f"vmotion_logfile_maxsize_bytes must be greater than 1024 (was {vmotion_logfile_maxsize_bytes}).")
        self._vmotion_logfile_maxsize_bytes = vmotion_logfile_maxsize_bytes

    @property
    def vmotion_logfile_count(self) -> int:
        return self._vmotion_logfile_count

    @vmotion_logfile_count.setter
    def vmotion_logfile_count(self, vmotion_logfile_count: int):
        if vmotion_logfile_count < 2:
            raise ValueError(f"vmotion_logfile_count must be greater than 1 (was {vmotion_logfile_count}).")
        self._vmotion_logfile_count = vmotion_logfile_count

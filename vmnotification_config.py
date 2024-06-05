import configparser


class VMNotificationConfig(object):
    DEFAULT_APP_NAME = "demo"
    DEFAULT_CHECK_INTERVAL_SECONDS = 1
    DEFAULT_TOKEN_FILE = "/var/run/vmotion_notifier/token_file"
    DEFAULT_LOG_LEVEL = "DEBUG"
    DEFAULT_CONSOLE_LEVEL = "WARNING"
    DEFAULT_LOGFILE = "/var/log/vmotion_notification/vmotion_notification.log"
    DEFAULT_LOGFILE_MAXSIZE_BYTES = 20 * 1024 * 1024
    DEFAULT_LOGFILE_COUNT = 10

    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

        self.app_name = self.config.get(section="DEFAULT",
                                        option="app_name",
                                        fallback=self.DEFAULT_APP_NAME)

        self.check_interval_seconds = self.config.getint(section="DEFAULT",
                                                         option="check_interval_seconds",
                                                         fallback=self.DEFAULT_CHECK_INTERVAL_SECONDS)

        self.token_file = self.config.get(section="DEFAULT",
                                          option="token_file",
                                          fallback=self.DEFAULT_TOKEN_FILE)

        self.pre_vmotion_cmd = self.config.get(section="DEFAULT",
                                               option="pre_vmotion_cmd")

        self.post_vmotion_cmd = self.config.get(section="DEFAULT",
                                                option="post_vmotion_cmd")

        self.log_level = self.config.get(section="Logging",
                                         option="log_level",
                                         fallback=self.DEFAULT_LOG_LEVEL)

        self.console_level = self.config.get(section="Logging",
                                             option="console_level",
                                             fallback=self.DEFAULT_CONSOLE_LEVEL)

        self.logfile = self.config.get(section="Logging",
                                       option="logfile",
                                       fallback=self.DEFAULT_LOGFILE)

        self.logfile_maxsize_bytes = self.config.getint(section="DEFAULT",
                                                        option="logfile_maxsize_bytes",
                                                        fallback=self.DEFAULT_LOGFILE_MAXSIZE_BYTES)

        self.logfile_count = self.config.getint(section="DEFAULT",
                                                option="logfile_count",
                                                fallback=self.DEFAULT_LOGFILE_COUNT)

    def print(self):
        print(f"Config file          : { self.config_file }\n"
              f"App name             : { self.app_name }\n"
              f"Check interval       : {self.check_interval_seconds} seconds\n"
              f"Token file           : {self.token_file}\n"
              f"Pre vMotion command  : {self.pre_vmotion_cmd}\n"
              f"Post vMotion command : {self.post_vmotion_cmd}\n"
              f"Log level            : {self.log_level}\n"
              f"Console level        : {self.console_level}\n"
              f"Logfile              : {self.logfile}\n"
              f"Logfile max size     : {self.logfile_maxsize_bytes} bytes\n"
              f"Logfile count        : {self.logfile_count}")

    @property
    def app_name(self) -> str:
        return self._app_name

    @app_name.setter
    def app_name(self, app_name: str):
        self._app_name = app_name

    @property
    def check_interval_seconds(self) -> int:
        return self._check_interval_seconds

    @check_interval_seconds.setter
    def check_interval_seconds(self, check_interval_seconds: int):
        if check_interval_seconds < 1:
            raise ValueError(f"check_interval_seconds must be greater than 0 (was {check_interval_seconds}).")
        self._check_interval_seconds = check_interval_seconds

    @property
    def token_file(self) -> str:
        return self._token_file

    @token_file.setter
    def token_file(self, token_file: str):
        self._token_file = token_file

    @property
    def pre_vmotion_cmd(self) -> str:
        return self._pre_vmotion_cmd

    @pre_vmotion_cmd.setter
    def pre_vmotion_cmd(self, pre_vmotion_cmd: str):
        self._pre_vmotion_cmd = pre_vmotion_cmd

    @property
    def post_vmotion_cmd(self) -> str:
        return self._post_vmotion_cmd

    @post_vmotion_cmd.setter
    def post_vmotion_cmd(self, post_vmotion_cmd: str):
        self._post_vmotion_cmd = post_vmotion_cmd

    @property
    def log_level(self) -> str:
        return self._log_level

    @log_level.setter
    def log_level(self, log_level: str):
        self._log_level = log_level

    @property
    def logfile(self) -> str:
        return self._logfile

    @logfile.setter
    def logfile(self, logfile: str):
        self._logfile = logfile

    @property
    def console_level(self) -> str:
        return self._console_level

    @console_level.setter
    def console_level(self, console_level: str):
        self._console_level = console_level

    @property
    def logfile_maxsize_bytes(self) -> int:
        return self._logfile_maxsize_bytes

    @logfile_maxsize_bytes.setter
    def logfile_maxsize_bytes(self, logfile_maxsize_bytes: int):
        if logfile_maxsize_bytes < 1:
            raise ValueError(f"check_interval_seconds must be greater than 1024 (was {logfile_maxsize_bytes}).")
        self._logfile_maxsize_bytes = logfile_maxsize_bytes

    @property
    def logfile_count(self) -> int:
        return self._logfile_count

    @logfile_count.setter
    def logfile_count(self, logfile_count: int):
        if logfile_count < 1:
            raise ValueError(f"check_interval_seconds must be greater than 0 (was {logfile_count}).")
        self._logfile_count = logfile_count

#! /usr/bin/python3
import configparser
import json
import logging
import logging.handlers
import shlex
import signal

from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
from time import sleep

logger = logging.getLogger(__name__)


def get_logging_level(level: str):
    level = level.upper()
    if level == "DEBUG":
        return logging.DEBUG
    if level == "INFO":
        return logging.INFO
    if level == "WARNING":
        return logging.WARNING
    if level == "ERROR":
        return logging.ERROR
    if level == "CRITICAL":
        return logging.CRITICAL

    # Default
    return logging.DEBUG


def create_logger(logfile: str, log_level: int, console_level: int, logfile_maxsize_bytes: int, logfile_count: int):

    # Set logging level
    logger.setLevel(log_level)

    # Set log format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)

    # Create file handler
    file_handler = logging.handlers.RotatingFileHandler(logfile,
                                                        maxBytes=logfile_maxsize_bytes,
                                                        backupCount=logfile_count)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def create_folders(folder_path: str):
    try:
        Path(folder_path).parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print(f"Insufficient permissions to create folder '{ folder_path }'")
        exit(1)


class VMotionConfig(object):
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


class VMotionNotificationException(Exception):
    def __init__(self, message: str):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class VMotionNotification(object):
    VMTOOLSD_CMD = "vmtoolsd --cmd "
    RPC_REGISTER_CMD = "vm-operation-notification.register"
    RPC_UNREGISTER_CMD = "vm-operation-notification.unregister"
    RPC_CHECK_EVENT_CMD = "vm-operation-notification.check-for-event"
    RPC_ACK_EVENT_CMD = "vm-operation-notification.ack-event"
    RPC_LIST_CMD = "vm-operation-notification.list"

    def __init__(self,
                 pre_vmotion_cmd: str,
                 post_vmotion_cmd: str,
                 token_file: str,
                 app_name: str = "demo",
                 check_interval_seconds: int = 1):
        logger.debug(
            f"VMotionNotification.__init__: [{pre_vmotion_cmd}, {post_vmotion_cmd}, {token_file}, {app_name}, {check_interval_seconds}]")
        self.pre_vmotion_cmd = pre_vmotion_cmd
        self.pre_vmotion_cmd_split = shlex.split(pre_vmotion_cmd)
        self.post_vmotion_cmd = post_vmotion_cmd
        self.post_vmotion_cmd_split = shlex.split(post_vmotion_cmd)
        self.app_name = app_name
        self.check_interval_seconds = check_interval_seconds
        self.token_file = token_file
        self.__token = None
        self.__run = True
        logger.debug(f"VMotionNotification.__init__: pre_vmotion_cmd_split: {self.pre_vmotion_cmd_split}")
        logger.debug(f"VMotionNotification.__init__: post_vmotion_cmd_split: {self.post_vmotion_cmd_split}")

    def read_token(self):
        logger.debug(f"VMotionNotification.read_token: Reading token: {self.token_file}")
        try:
            with Path(self.token_file).open(mode='r', encoding="utf-8") as f:
                self.__token = f.readline()
            logger.debug(f"VMotionNotification.read_token: Read token: {self.__token}")
        except FileNotFoundError as e:
            logger.debug(f"VMotionNotification.read_token: '{ e }'")
            logger.debug(f"VMotionNotification.read_token: File does not exist: {self.token_file}")

    def write_token(self):
        logger.debug(f"VMotionNotification.write_token: Write token: {self.__token} to file: {self.token_file}")
        try:
            p = Path(self.token_file)
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open(mode='w', encoding ="utf-8") as f:
                f.write(self.__token)

        except PermissionError as e:
            logger.warning(f"VMotionNotification.write_token: {e}")
            logger.warning(f"VMotionNotification.write_token: Could not save token to file.")

        except Exception as e:
            logger.debug(f"VMotionNotification.write_token: {e}")
            raise e

    def delete_token(self):
        try:
            logger.debug(f"VMotionNotification.delete_token: Deleting token at { self.token_file }")
            Path(self.token_file).unlink()

        except PermissionError as e:
            logger.error(f"VMotionNotification.delete_token: {e}")
            logger.error(f"VMotionNotification.delete_token: Could not delete the token to file at { self.token_file }")

        except FileNotFoundError as e:
            logger.debug(f"VMotionNotification.delete_token: {e}")
            logger.debug(f"VMotionNotification.delete_token: No token file to delete at { self.token_file }")

    @classmethod
    def run_rpc(cls, rpc_name: str, params: dict):
        try:
            from shlex import quote
        except ImportError:
            from pipes import quote

        # handle none param dict
        param = ""
        if params is not None:
            param = json.dumps(params)
        cmd = cls.VMTOOLSD_CMD + quote(rpc_name + " " + param)

        logger.debug(f"VMotionNotification.run_rpc: Running cmd : {cmd}")

        output = Popen(shlex.split(cmd), stdout=PIPE, stderr=STDOUT)
        stdout = output.communicate()
        reply = json.loads(stdout[0])
        if not reply.get("result"):
            error_message = reply.get("errorMessage")
            logger.fatal(f"VMotionNotification.run_rpc: '{error_message}'")
            raise VMotionNotificationException(error_message)

        return reply

    def run_pre_vmotion(self):
        logger.debug(f"VMotionNotification.run_pre_vmotion: Running cmd : '{self.pre_vmotion_cmd_split}'")
        output = Popen(self.pre_vmotion_cmd_split, stdout=PIPE, stderr=STDOUT)
        for line in output.stdout:
            line_striped = line.rstrip(b"\n")
            logger.debug(f"VMotionNotification.run_pre_vmotion: '{line_striped}'")
        output.wait()
        logger.debug(f"VMotionNotification.run_pre_vmotion: Command completed.")

    def run_post_vmotion(self):
        logger.debug(f"VMotionNotification.run_post_vmotion: Running cmd : '{self.post_vmotion_cmd_split}'")
        output = Popen(self.post_vmotion_cmd_split, stdout=PIPE, stderr=STDOUT)
        for line in output.stdout:
            line_striped = line.rstrip(b"\n")
            logger.debug(f"VMotionNotification.run_post_vmotion: '{line_striped}'")
        output.wait()
        logger.debug(f"VMotionNotification.run_post_vmotion: Command completed.")

    def register_for_notification(self):
        """
        Possible Registration Errors
        - vm-operation-notification.register: Invalid input: Failed to register additional apps.
          Max allowed limit of 1 concurrent apps already registered., please see schema for detail and examples
        - vm-operation-notification.register: Invalid input: VM operation notification not enabled on this VM,
          please see schema for detail and examples
        - vm-operation-notification.unregister: Invalid input: Could not find application with the token.,
          please see schema for detail and examples
        """
        params = {"appName": self.app_name, "notificationTypes": ["sla-miss"]}
        reply = self.run_rpc(self.RPC_REGISTER_CMD, params)
        unique_token = reply.get("uniqueToken")

        if not unique_token:
            error_msg = "No token was returned."
            logger.fatal(f"VMotionNotification.register_for_notification: {error_msg}")
            raise VMotionNotificationException(error_msg)

        logger.debug(f"VMotionNotification.register_for_notification: Token returned on registration: '{unique_token}'")

        return unique_token

    def unregister_for_notification(self):
        """
        Possible Unregistration Errors
        - vm-operation-notification.unregister: Invalid input: Could not find application with the token.,
          please see schema for detail and examples
        """
        if not self.__token:
            logger.debug(f"VMotionNotification.unregister_for_notification: No token to unregister")
            return

        logger.debug(f"VMotionNotification.unregister_for_notification: Unregister token {self.__token}")
        params = {"uniqueToken": self.__token}
        reply = self.run_rpc(self.RPC_UNREGISTER_CMD, params)
        logger.debug(f"VMotionNotification.unregister_for_notification: Received reply: {reply}")
        logger.debug(f"VMotionNotification.unregister_for_notification: Unregistered token {self.__token}")

    def ack_event(self, op_id: str):
        logger.debug(f"VMotionNotification.ack_event: Token '{self.__token}', operationId: '{op_id}'")
        params = {"uniqueToken": self.__token, "operationId": op_id}
        logger.debug(f"VMotionNotification.ack_event: Acknowledging notification.")
        reply = self.run_rpc(self.RPC_ACK_EVENT_CMD, params)
        logger.debug(f"VMotionNotification.ack_event: Received reply: {reply}")
        logger.debug(f"VMotionNotification.ack_event: Acknowledged.")

    def check_for_events(self):
        self.__run = True
        params = {"uniqueToken": self.__token}
        logger.debug(f"VMotionNotification.check_for_events: params: '{params}'.")

        while self.__run:
            reply = self.run_rpc(self.RPC_CHECK_EVENT_CMD, params)
            event_type = reply.get("eventType", None)

            if event_type == "start":
                op_id = reply.get("operationId")
                notification_timeout = reply.get("notificationTimeoutInSec")
                logger.debug(f"VMotionNotification.check_for_events: "
                             f"Motion start notification for migration id with operationId: '{op_id}'.")
                logger.debug(f"VMotionNotification.check_for_events: '"
                             f"Notification timeout: '{notification_timeout}' seconds.")
                print(f"vMotion start with operation ID '{op_id}' and timeout of {notification_timeout} seconds.")

                # Invoke PRE vMotion operation
                self.run_pre_vmotion()

                # Ack start event
                self.ack_event(op_id)

            elif event_type == "timeout-change":
                op_id = reply.get("operationId")
                notification_timeout = reply.get("newNotificationTimeoutInSec")

                logger.debug(f"VMotionNotification.check_for_events: "
                             f"Notification timeout change event received.")
                logger.debug(f"VMotionNotification.check_for_events: '"
                             f"New notification timeout: '{notification_timeout}' seconds.")

                self.ack_event(op_id)

            elif event_type == "end":
                op_id = reply.get("operationId")
                logger.debug(f"VMotionNotification.check_for_events: "
                             f"vMotion end notification for migration id '{op_id}'.")
                print(f"vMotion end with operation ID '{op_id}'")

                # Invoke POST vMotion operation
                self.run_post_vmotion()

            # poll interval
            sleep(self.check_interval_seconds)

    def run(self):

        # Setup signal handlers for SIGINT and SIGTERM
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        try:
            # Cleanup in case a previous instance was not terminated cleanly
            self.read_token()
            self.unregister_for_notification()
        except FileNotFoundError:
            logger.debug(f"VMotionNotification.run: No existing tokens to unregister.")
        except VMotionNotificationException as e:
            logger.debug(f"VMotionNotification.run: { e }")

        try:
            # Register for notification
            self.__token = self.register_for_notification()

            # Write token to file
            self.write_token()

            # Check for vmotion events
            self.check_for_events()

        except VMotionNotificationException as e:
            logger.fatal(f"VMotionNotification.run: {e}")

        except Exception as e:
            logger.fatal(f"VMotionNotification.run: Unexpected exception: {e}")

        except:
            logger.fatal(f"Caught exception.")

        finally:
            logger.debug(f"VMotionNotification.run: Cleaning up")
            self.unregister_for_notification()
            self.delete_token()

    def stop(self, signum=None, frame=None):
        signame = signal.Signals(signum).name
        logger.debug(f"VMotionNotification.stop: Received stop request from {signame}")
        self.__run = False


def main():

    # Check if configuration file exists
    config_file = "/etc/vmotion_notification.conf"
    if not (Path(config_file).is_file() and Path(config_file).exists()):
        print(f"Configuration file is missing: '{ config_file }'")
        exit(1)

    # Parse configuration file
    config = VMotionConfig(config_file=config_file)
    config.print()

    # Create required folders
    create_folders(config.logfile)
    create_folders(config.token_file)

    # Create logger
    create_logger(logfile=config.logfile,
                  log_level=get_logging_level(config.log_level),
                  console_level=get_logging_level(config.console_level),
                  logfile_maxsize_bytes=config.logfile_maxsize_bytes,
                  logfile_count=config.logfile_count)

    logger.debug("Starting vMotion notification service.")
    logger.debug(f"Application pre migration command: '{config.pre_vmotion_cmd}'")
    logger.debug(f"Application pre migration command: '{config.post_vmotion_cmd}'")
    vmn = VMotionNotification(pre_vmotion_cmd=config.pre_vmotion_cmd,
                              post_vmotion_cmd=config.post_vmotion_cmd,
                              token_file=config.token_file,
                              app_name=config.app_name,
                              check_interval_seconds=config.check_interval_seconds)
    vmn.run()


if __name__ == "__main__":
    main()

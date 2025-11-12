import datetime
import json
import logging
import re
import shlex
import signal
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT
from time import sleep

from vmnotification_exception import VMNotificationException

logger = logging.getLogger(__name__)
logger_vmotion = logging.getLogger('vmotion')
logger_timeout = logging.getLogger('timeout')


class VMNotificationService(object):
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
                 check_interval_seconds: int = 1,
                 token_file_create: bool = True,
                 token_obfuscate_logfile: bool = False,
                 ):
        logger.debug(
            f"__init__: ["
            f"{pre_vmotion_cmd},"
            f"{post_vmotion_cmd}, "
            f"{token_file}, "
            f"{app_name}, "
            f"{check_interval_seconds}, "
            f"{token_file_create}, "
            f"{token_obfuscate_logfile}]")
        self.pre_vmotion_cmd = pre_vmotion_cmd
        self.pre_vmotion_cmd_split = shlex.split(pre_vmotion_cmd)
        self.post_vmotion_cmd = post_vmotion_cmd
        self.post_vmotion_cmd_split = shlex.split(post_vmotion_cmd)
        self.token_file = token_file
        self.app_name = app_name
        self.check_interval_seconds = check_interval_seconds
        self.token_file_create = token_file_create
        self.token_obfuscate_logfile = token_obfuscate_logfile
        self.__token = None
        self.__run = True
        self.__ran_pre_cmd = False
        logger.debug(f"__init__: pre_vmotion_cmd_split: {self.pre_vmotion_cmd_split}")
        logger.debug(f"__init__: post_vmotion_cmd_split: {self.post_vmotion_cmd_split}")

    def _obfuscate_msg(self, msg: str):
        if self.token_obfuscate_logfile and self.__token:
            return re.sub(f"{self.__token}", f"{self.__token[0:8]}-{'*' * 4}-{'*' * 4}-{'*' * 4}-{'*' * 12}", msg)
        else:
            return msg

    def _debug(self, msg):
        logger.debug(self._obfuscate_msg(msg))

    def _info(self, msg):
        logger.info(self._obfuscate_msg(msg))

    def _warning(self, msg):
        logger.warning(self._obfuscate_msg(msg))

    def _error(self, msg):
        logger.error(self._obfuscate_msg(msg))

    def _critical(self, msg):
        logger.critical(self._obfuscate_msg(msg))

    def read_token(self):
        try:
            self._debug(f"read_token: Reading token: {self.token_file}")
            with Path(self.token_file).open(mode='r', encoding="utf-8") as f:
                self.__token = f.readline()
            self._debug(f"read_token: Read token: {self.__token}")
        except FileNotFoundError as e:
            self._debug(f"read_token: '{e}'")
            self._debug(f"read_token: File does not exist: {self.token_file}")

    def write_token(self):
        try:
            self._debug(f"write_token: Write token: {self.__token} to file: {self.token_file}")
            p = Path(self.token_file)
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open(mode='w', encoding ="utf-8") as f:
                f.write(self.__token)
            self._debug(f"write_token: Token written to file {self.token_file}")
        except PermissionError as e:
            self._error(f"write_token: {e}")
            self._error(f"write_token: Could not save token to file.")

        except Exception as e:
            self._error(f"write_token: {e}")
            raise e

    def delete_token(self):
        try:
            self._debug(f"delete_token: Deleting token at {self.token_file}")
            Path(self.token_file).unlink()

        except PermissionError as e:
            self._error(f"delete_token: {e}")
            self._error(f"delete_token: Could not delete the token to file at {self.token_file}")

        except FileNotFoundError as e:
            self._debug(f"delete_token: {e}")
            self._debug(f"delete_token: No token file to delete at {self.token_file}")

    def run_rpc(self, rpc_name: str, params: dict):
        from shlex import quote

        # handle none param dict
        param = ""
        if params is not None:
            param = json.dumps(params)
        cmd = self.VMTOOLSD_CMD + quote(rpc_name + " " + param)

        self._debug(f"run_rpc: Running cmd : {cmd}")

        output = Popen(shlex.split(cmd), stdout=PIPE, stderr=STDOUT)
        stdout = output.communicate()
        reply = json.loads(stdout[0])
        if not reply.get("result"):
            error_msg = reply.get('errorMessage')
            self._critical(f"run_rpc: {error_msg}")
            raise VMNotificationException(error_msg)

        return reply

    def run_pre_vmotion(self):
        self._debug(f"run_pre_vmotion: Running cmd : '{self.pre_vmotion_cmd_split}'")
        output = Popen(self.pre_vmotion_cmd_split, stdout=PIPE, stderr=STDOUT)
        for line in output.stdout:
            line_striped = line.rstrip(b"\n")
            self._debug(f"run_pre_vmotion: '{line_striped}'")
        output.wait()
        self._debug(f"run_pre_vmotion: Command completed.")

    def run_post_vmotion(self):
        self._debug(f"run_post_vmotion: Running cmd : '{self.post_vmotion_cmd_split}'")
        output = Popen(self.post_vmotion_cmd_split, stdout=PIPE, stderr=STDOUT)
        for line in output.stdout:
            line_striped = line.rstrip(b"\n")
            self._debug(f"run_post_vmotion: '{line_striped}'")
        output.wait()
        self._debug(f"run_post_vmotion: Command completed.")

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
            self._critical(f"register_for_notification: {error_msg}")
            raise VMNotificationException(error_msg)

        self._debug(f"register_for_notification: Registration successful.")

        return unique_token

    def unregister_for_notification(self):
        """
        Possible Unregistration Errors
        - vm-operation-notification.unregister: Invalid input: Could not find application with the token.,
          please see schema for detail and examples
        """
        if not self.__token:
            self._debug(f"unregister_for_notification: No token to unregister")
            return

        self._debug(f"unregister_for_notification: Unregister token {self.__token}")
        params = {"uniqueToken": self.__token}
        reply = self.run_rpc(self.RPC_UNREGISTER_CMD, params)

        self._debug(f"unregister_for_notification: Received reply: {reply}")
        self._debug(f"unregister_for_notification: Unregistered token {self.__token}")

    def ack_event(self, op_id: str):
        self._debug(f"ack_event: Token '{self.__token}', operationId: '{op_id}'")
        params = {"uniqueToken": self.__token, "operationId": op_id}
        self._debug(f"ack_event: Acknowledging notification.")
        reply = self.run_rpc(self.RPC_ACK_EVENT_CMD, params)
        self._debug(f"ack_event: Received reply: {reply}")
        self._debug(f"ack_event: Acknowledged.")

    def check_for_events(self):
        self.__run = True

        # A bit ugly, but workaround for obfuscation
        params = {"uniqueToken": self.__token}
        self._debug(f"check_for_events: params: '{params}'.")
        params = {"uniqueToken": self.__token}

        while self.__run:
            reply = self.run_rpc(self.RPC_CHECK_EVENT_CMD, params)
            event_type = reply.get("eventType", None)

            if event_type == "start":
                logger_vmotion.debug(f"{'-' * 60}")
                logger_vmotion.debug(f"vmotion start event: {reply}")
                op_id = reply.get("operationId")
                notification_timeout = reply.get("notificationTimeoutInSec")
                event_time_epoch = reply.get("eventGenTimeInSec")
                self._debug(f"check_for_events: vmotion notification with operationId: '{op_id}'")
                self._debug(f"check_for_events: notification timeout: '{notification_timeout}' seconds")
                self._debug(f"check_for_events: event time: '{datetime.datetime.fromtimestamp(event_time_epoch)}'")

                print(f"vmotion start with operation ID '{op_id}' and timeout of {notification_timeout} seconds.")

                event_time = datetime.datetime.fromtimestamp(event_time_epoch)
                time_now = datetime.datetime.now()

                if time_now < event_time + datetime.timedelta(0, notification_timeout):
                    # Invoke PRE vMotion operation
                    logger_vmotion.debug(f"pre-vmotion command starting: '{self.pre_vmotion_cmd}'")
                    self.run_pre_vmotion()
                    self.__ran_pre_cmd = True
                    logger_vmotion.debug(f"pre-vmotion command complete.")
                
                    # Ack start event
                    logger_vmotion.debug(f"acknowledging vmotion operation.")
                    self.ack_event(op_id)
                else:
                    # Stale event
                    self._warning(f"stale event - ignoring vmotion event with {op_id}")

            elif event_type == "timeout-change":
                op_id = reply.get("operationId")
                notification_timeout = reply.get("newNotificationTimeoutInSec")
                self._warning(f"check_for_events: Notification timeout change event received.")
                self._warning(f"check_for_events: new notification timeout: '{notification_timeout}' seconds.")

                # Update timeout logfile
                logger_timeout.warning(f"check_for_events: Notification timeout change event received.'")
                logger_timeout.warning(f"check_for_events: new notification timeout: '{notification_timeout}' seconds.")

                self.ack_event(op_id)

            elif event_type == "end":
                logger_vmotion.debug(f"vmotion end event: {reply}")
                self._debug(f"check_for_events: vMotion end notification for migration id '{reply.get('operationId')}'.")
                print(f"vMotion end with operation ID '{reply.get('operationId')}'")

                # Invoke POST vMotion operation
                if self.__ran_pre_cmd:
                    logger_vmotion.debug(f"post-vmotion command starting: '{self.post_vmotion_cmd}'.")
                    self.run_post_vmotion()
                    self.__ran_pre_cmd = False
                    logger_vmotion.debug(f"post-vmotion command complete.")
                else:
                    self._warning(f"pre command not run, not running post command")

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
            self._debug(f"run: No existing tokens to unregister.")
        except VMNotificationException as e:
            self._debug(f"run: {e}")

        try:
            # Register for notification
            self.__token = self.register_for_notification()

            # Write token to file
            if self.token_file_create:
                self.write_token()

            # Check for vmotion events
            self.check_for_events()

        except VMNotificationException as e:
            self._critical(f"run: {e}")

        except Exception as e:
            self._critical(f"run: Unexpected exception: {e}")

        finally:
            self._debug(f"run: Cleaning up")
            self.unregister_for_notification()
            self.delete_token()

    def stop(self, signum=None, frame=None):
        signame = signal.Signals(signum).name
        self._debug(f"stop: Received stop request from {signame}")
        self.__run = False

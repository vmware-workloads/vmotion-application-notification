#! /usr/bin/python3
import json
import logging
import logging.handlers
import shlex

from subprocess import Popen, PIPE, STDOUT
from time import sleep


logger = logging.getLogger(__name__)


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

    def __init__(self, pre_vmotion_cmd: str, post_vmotion_cmd: str, app_name: str = "demo"):
        logger.debug(f"VMotionNotification.__init__: [{ pre_vmotion_cmd }, { post_vmotion_cmd }, { app_name } ]")
        self.pre_vmotion_cmd = pre_vmotion_cmd
        self.pre_vmotion_cmd_split = shlex.split(pre_vmotion_cmd)
        self.post_vmotion_cmd = post_vmotion_cmd
        self.post_vmotion_cmd_split = shlex.split(post_vmotion_cmd)
        self.app_name = app_name
        self.__token = None
        logger.debug(f"VMotionNotification.__init__: pre_vmotion_cmd_split: { self.pre_vmotion_cmd_split }")
        logger.debug(f"VMotionNotification.__init__: post_vmotion_cmd_split: { self.post_vmotion_cmd_split }")

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

        logger.debug(f"VMotionNotification.run_rpc: Running cmd : { cmd }")

        output = Popen(shlex.split(cmd), stdout=PIPE, stderr=STDOUT)
        stdout = output.communicate()
        reply = json.loads(stdout[0])
        if not reply.get("result"):
            error_message = reply.get("errorMessage")
            logger.fatal(f"VMotionNotification.run_rpc: '{ error_message }'")
            raise VMotionNotificationException(error_message)

        return reply

    def run_pre_vmotion(self):
        logger.debug(f"VMotionNotification.run_pre_vmotion: Running cmd : '{ self.pre_vmotion_cmd_split }'")
        output = Popen(self.pre_vmotion_cmd_split, stdout=PIPE, stderr=STDOUT)
        for line in output.stdout:
            line_striped = line.rstrip(b"\n")
            logger.debug(f"VMotionNotification.run_pre_vmotion: '{ line_striped }'")
        output.wait()
        logger.debug(f"VMotionNotification.run_pre_vmotion: Command completed.")

    def run_post_vmotion(self):
        logger.debug(f"VMotionNotification.run_post_vmotion: Running cmd : '{self.post_vmotion_cmd_split}'")
        output = Popen(self.post_vmotion_cmd_split, stdout=PIPE, stderr=STDOUT)
        for line in output.stdout:
            line_striped = line.rstrip(b"\n")
            logger.debug(f"VMotionNotification.run_post_vmotion: '{ line_striped }'")
        output.wait()
        logger.debug(f"VMotionNotification.run_post_vmotion: Command completed.")

    def register_for_notification(self):
        """
        Possible Registration Errors
        - vm-operation-notification.register: Invalid input: Failed to register additional apps.
          Max allowed limit of 1 concurrent apps already registered., please see schema for detail and examples
        - vm-operation-notification.register: Invalid input: VM operation notification not enabled on this VM,
          please see schema for detail and examples
        """
        params = {"appName": self.app_name, "notificationTypes": ["sla-miss"]}
        reply = self.run_rpc(self.RPC_REGISTER_CMD, params)
        unique_token = reply.get("uniqueToken")
        logger.debug(f"VMotionNotification.register_for_notification: Token returned on registration: '{ unique_token }'")

        if not unique_token:
            error_msg = "No token was returned."
            logger.fatal(f"VMotionNotification.register_for_notification: { error_msg }")
            raise VMotionNotificationException(error_msg)

        return unique_token

    def unregister_for_notification(self):
        if not self.__token:
            logger.debug(f"VMotionNotification.unregister_for_notification: No token to unregister")
            return

        logger.debug(f"VMotionNotification.unregister_for_notification: Unregister token { self.__token }")
        params = {"uniqueToken": self.__token}
        reply = self.run_rpc(self.RPC_UNREGISTER_CMD, params)
        logger.debug(f"VMotionNotification.unregister_for_notification: Received reply: { reply }")
        logger.debug(f"VMotionNotification.unregister_for_notification: Unregistered token { self.__token }")

    def ack_event(self, op_id: str):
        logger.debug(f"VMotionNotification.ack_event: Token '{self.__token}', operationId: '{ op_id }'")
        params = {"uniqueToken": self.__token, "operationId": op_id}
        logger.debug(f"VMotionNotification.ack_event: Acknowledging notification.")
        reply = self.run_rpc(self.RPC_ACK_EVENT_CMD, params)
        logger.debug(f"VMotionNotification.ack_event: Received reply: { reply }")
        logger.debug(f"VMotionNotification.ack_event: Acknowledged.")

    def check_for_events(self):
        check_for_event = True
        params = {"uniqueToken": self.__token}
        logger.debug(f"VMotionNotification.check_for_events: params: '{ params }'.")

        while check_for_event:
            reply = self.run_rpc(self.RPC_CHECK_EVENT_CMD, params)
            event_type = reply.get("eventType", None)

            if event_type == "start":
                op_id = reply.get("operationId")
                notification_timeout = reply.get("notificationTimeoutInSec")

                logger.debug(f"VMotionNotification.check_for_events: "
                             f"Motion start notification for migration id with operationId: '{ op_id }'.")
                logger.debug(f"VMotionNotification.check_for_events: '"
                             f"Notification timeout: '{ notification_timeout }' seconds.")

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
                             f"vMotion end notification for migration id '{ op_id }'.")

                # Invoke POST vMotion operation
                self.run_post_vmotion()

            # poll interval
            sleep(1)

    def run(self):

        try:
            # Register for notification
            self.__token = self.register_for_notification()

            # Check for vmotion events
            self.check_for_events()

        except VMotionNotificationException as e:
            logger.fatal(f"VMotionNotification.run: { e }")

        except KeyboardInterrupt:
            logger.debug(f"VMotionNotification.run: Caught 'CTRL-C'")

        except:
            logger.debug(f"Caught exception.")

        finally:
            logger.debug(f"VMotionNotification.run: Running finally.")
            self.unregister_for_notification()


def main():

    LOG_FILENAME = 'logging_rotatingfile_example.log'
    PRE_CMD = 'ping -c 20 8.8.8.8'
    POST_CMD = 'ping -c 10 8.8.8.8'

    logger.setLevel(logging.DEBUG)

    # Add the log message handler to the logger
    file_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=20000, backupCount=10)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.debug("Starting vMotion notification service.")
    logger.debug(f"Application pre migration command: '{ PRE_CMD }'")
    logger.debug(f"Application pre migration command: '{ POST_CMD }'")
    vmn = VMotionNotification(pre_vmotion_cmd="ls", post_vmotion_cmd="ls")
    vmn.run()


if __name__ == "__main__":
    main()

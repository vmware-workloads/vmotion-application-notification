#! /usr/bin/env python3
import argparse
import logging
import logging.handlers

from pathlib import Path

from utils import create_folders, get_logging_level
from vmnotification_config import VMNotificationConfig


def create_logger(logger_name: str,
                  logfile: str,
                  log_level: int,
                  console_level: int,
                  logfile_maxsize_bytes: int,
                  logfile_count: int) -> logging.Logger:

    logger = logging.getLogger(logger_name)

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

    return logger


def main():

    # Get CLI input
    parser = argparse.ArgumentParser(prog='vmnotification', description='vMotion Notification for Linux')
    parser.add_argument('-c', '--config', type=str, required=True)
    args = parser.parse_args()
    config_file = args.config

    # Check if a configuration file exists
    if not (Path(config_file).is_file() and Path(config_file).exists()):
        print(f"Configuration file is missing: '{config_file}'")
        parser.print_help()
        exit(1)

    # Parse configuration file
    config = VMNotificationConfig(config_file=config_file)
    config.print()

    # Create required folders
    create_folders(config.service_logfile)
    create_folders(config.vmotion_logfile)
    create_folders(config.timeout_logfile)
    create_folders(config.token_file)

    # Create logger
    logger = create_logger(logger_name='',
                           logfile=config.service_logfile,
                           log_level=get_logging_level(config.service_logfile_level),
                           console_level=get_logging_level(config.service_console_level),
                           logfile_maxsize_bytes=config.service_logfile_maxsize_bytes,
                           logfile_count=config.service_logfile_count)

    logger_vmotion = create_logger(logger_name='vmotion',
                                   logfile=config.vmotion_logfile,
                                   log_level=get_logging_level("DEBUG"),
                                   console_level=get_logging_level("DEBUG"),
                                   logfile_maxsize_bytes=config.vmotion_logfile_maxsize_bytes,
                                   logfile_count=config.vmotion_logfile_count)

    logger_timeout = create_logger(logger_name='timeout',
                                   logfile=config.timeout_logfile,
                                   log_level=get_logging_level("DEBUG"),
                                   console_level=get_logging_level("DEBUG"),
                                   logfile_maxsize_bytes=config.timeout_logfile_maxsize_bytes,
                                   logfile_count=config.timeout_logfile_count)

    from vmnotification_service import VMNotificationService

    logger.debug("Starting vMotion notification service")
    logger.debug(f"Config: {config.json()}")
    logger.debug(f"Application pre migration command: '{config.pre_vmotion_cmd}'")
    logger.debug(f"Application post migration command: '{config.post_vmotion_cmd}'")
    vmn = VMNotificationService(pre_vmotion_cmd=config.pre_vmotion_cmd,
                                post_vmotion_cmd=config.post_vmotion_cmd,
                                token_file=config.token_file,
                                app_name=config.app_name,
                                check_interval_seconds=config.check_interval_seconds,
                                token_file_create=config.token_file_create,
                                token_obfuscate_logfile=config.token_obfuscate_logfile)
    vmn.run()


if __name__ == "__main__":
    main()

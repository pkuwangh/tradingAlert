#!/usr/bin/env python

import logging

from drive_builder import build_history
from drive_hunter import hunt_option_activity
from drive_tracker import track_option_effect
from utils_logging import get_root_dir, setup_logger, setup_metadata_dir

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def schedule_run():
    hunt_option_activity()
    # TODO: use cache from hunter
    build_history()
    track_option_effect()


if __name__ == '__main__':
    metadata_dir = setup_metadata_dir()
    setup_logger(__file__)
    logger.setLevel(logging.INFO)
    schedule_run()
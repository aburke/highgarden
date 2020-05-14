"""
Module exists to provide functions to demo airflow dags.
"""
import logging


def do_one_thing() -> None:
    ''' Dummy methode for demo dag '''
    logging.info('Doing one task')


def do_some_others(loop_count: int) -> None:
    ''' Dummy methode for demo dag '''
    import time
    logging.info("Yea more stuff is happening.")
    logging.info("And it is going to be great.")
    for i in range(loop_count):
        logging.info("{} mississippi".format(i))
        time.sleep(1)


def finish_up() -> None:
    ''' Dummy methode for demo dag '''
    logging.info("Ok this is over.")

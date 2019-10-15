import inspect
from robot.conf import RobotSettings
from robot.api import logger
from robot.variables import VariableScopes
from robot.running.timeouts import KeywordTimeout
from robot.libraries.BuiltIn import BuiltIn


BuiltIn().import_library('pabot.PabotLib')
PABOT = BuiltIn().get_library_instance('pabot.PabotLib')


# if both timeout and log decorator is used for one function, timeout decorator should be used first


def robot_timeout(timeoutinseconds):
    def timeout_decorator(func):
        def wrapper(*args, **kwargs):
            timeout_msg = func.__name__ + " timed out !!"
            timeout = KeywordTimeout(timeoutinseconds, timeout_msg, VariableScopes(RobotSettings()))
            timeout.start()
            return timeout.run(func, args, kwargs)

        return wrapper

    return timeout_decorator


def robot_log(func):
    def wrapper(*args, **kwargs):
        spec = inspect.getargspec(func)
        for key in kwargs.iterkeys():
            if key not in spec.args:
                # if function is called from robot, and one of it's unnamed string parameters has '=' in it
                # move this parameter from kwargs to args
                l = list(args)
                b = '{0}={1}'.format(key, kwargs[key])
                l.append(b)
                args = tuple(l)
                kwargs.pop(key)

        argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
        parameters = ": "
        for entry in zip(argnames, args) + kwargs.items():
            if 'self' not in entry:
                parameters += ('%s=%r, ' % entry)
        fname = func.func_name
        logger.info("<span class='label pass'><span style='font-size: 1.25em'>ENTER: " + fname +
                    "</span></span>" + parameters, html=True)
        result = func(*args, **kwargs)
        logger.info("<span class='label warn'><span style='font-size: 1.25em'>EXIT: " + fname +
                    "</span></span>", html=True)
        return result

    return wrapper


def pabot_lock(lock_name):
    """Sets Pabot lock until the execution of the function
    pabot_lock should be used after the robot_log if both function decorators are used at the same time"""

    def pabot_lock_decorator(func):
        def wrapper(*args, **kwargs):
            PABOT.acquire_lock(lock_name)
            logger.info(lock_name + " lock acquired on " + func.__name__)
            result = None
            try:
                result = func(*args, **kwargs)
            finally:
                PABOT.release_lock(lock_name)
                logger.info(lock_name + " lock released from " + func.__name__)
            return result

        return wrapper

    return pabot_lock_decorator

#coding: utf-8

# Async function calls
# from: http://micheles.googlecode.com/hg/decorator/documentation.html
import itertools, decorator
class Async(object):
    """
    A decorator converting blocking functions into asynchronous
    functions, by using threads or processes. Examples:

    async_with_threads =  Async(threading.Thread)
    async_with_processes =  Async(multiprocessing.Process)
    """
    def on_success(result): # default implementation
        "Called on the result of the function"
        return result
    
    def on_failure(exc_info): # default implementation
        "Called if the function fails"
        pass
    
    def on_closing(): # default implementation
        "Called at the end, both in case of success and failure"
        pass
    
    def __init__(self, threadfactory):
        self.threadfactory = threadfactory

    def __call__(self, func, on_success=on_success,
                 on_failure=on_failure, on_closing=on_closing):
        # every decorated function has its own independent thread counter
        func.counter = itertools.count(1)
        func.on_success = on_success
        func.on_failure = on_failure
        func.on_closing = on_closing
        return decorator.decorator(self.call, func)

    def call(self, func, *args, **kw):
        def func_wrapper():
            try:
                result = func(*args, **kw)
            except:
                func.on_failure(sys.exc_info())
            else:
                return func.on_success(result)
            finally:
                func.on_closing()
        name = '%s-%s' % (func.__name__, func.counter.next())
        thread = self.threadfactory(None, func_wrapper, name)
        thread.start()
        return thread

import threading
async_thread = Async(threading.Thread)
try:
    import multiprocessing
    async_process = Async(multiprocessing.Process)
except ImportError:
    async_process = async_thread


def synchronized(lock):
    """ Synchronization decorator. """

    def wrap(f):
        def new_function(*args, **kw):
            lock.acquire()
            try:
                return f(*args, **kw)
            finally:
                lock.release()
        return new_function
    return wrap


class IsNotTheOneException(Exception):
    message = 'This is not the only thread alive. So, got killed.'

def synchronized_highlander(semaphore):
    """ Synchronization decorator - highlander style:
    
    If the semaphore is red, the thread trying to acquire it is killed,
    so only one thread will be alive for the semaphore.
    """

    def wrap(f):
        def new_function(*args, **kw):
            can_run = semaphore.acquire(False)
            if can_run:
                try:
                    return f(*args, **kw)
                finally:
                    semaphore.release()
            else:
                raise IsNotTheOneException()
        return new_function
    return wrap
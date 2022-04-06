from signal import SIG_IGN, SIGQUIT, signal
from signal import alarm
from signal import SIGALRM
from signal import SIGINT
from signal import SIG_IGN
from signal import SIGTSTP
from signal import SIGTERM
from signal import SIGQUIT
from sys import exit


USER_RES_TIMEOUT = 12
USER_MENU_TIMEOUT = 15

    
def catchthesignal(signal, frame):
    print('\n Keyboard Interrupt caught...exiting..')
    exit(0)

def init_keyboard_catch():
    signal(SIGINT, catchthesignal) 
    signal(SIGTERM, catchthesignal)
    signal(SIGQUIT, catchthesignal)
    signal(SIGTSTP, catchthesignal)

def timeout_error(*_):
    print("\n CLIENT TOOK TOO LONG TO RESPOND")
    raise TimeoutError
        
    
def init_timeout_err():
    print("Please respond in", USER_RES_TIMEOUT, " seconds ")
    signal(SIGALRM, timeout_error)
    alarm(USER_RES_TIMEOUT)
    
def remove_timeout_err():
    signal(SIGALRM,SIG_IGN)
    alarm(0)


def timeout_menu_error(*_):
    raise TimeoutError
        
    
def init_timeout_menu_err():
    signal(SIGALRM, timeout_menu_error)
    alarm(USER_MENU_TIMEOUT)
    
    
    

    

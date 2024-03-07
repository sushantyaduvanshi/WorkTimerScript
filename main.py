from pynput.keyboard import Listener as key_listener
from pynput.mouse import Listener as mouse_listener
from threading import Thread
from pygame import mixer
from time import time, sleep

work_time_span = 45 * 60 # in sec
rest_time_span = 10 * 60 # in sec

last_activity_detected_on = time()
work_timer_started = False
rest_timer_started = False
timer_thread = None
interrupt_timer_thread = False

mixer.init()
mixer.music.load("./Alert.mp3")

def detected_activity(*args):
    global last_activity_detected_on, timer_thread, interrupt_timer_thread
    last_time = last_activity_detected_on
    last_activity_detected_on = time()
    if work_timer_started and (time()-last_time) >= rest_time_span:
        # cheat rest detected
        interrupt_timer_thread = True
        print("Waiting previous thread to join..")
        timer_thread.join()
    elif rest_timer_started:
        # start beep sound
        mixer.music.play()
    elif not work_timer_started and not rest_timer_started:
        if(timer_thread and timer_thread.is_alive()):
            interrupt_timer_thread = True
            print("Waiting previous thread to join..")
            timer_thread.join()
        timer_thread = Thread(target=start_work_timer)
        print("New timer thread started!!!")
        timer_thread.start()

def start_work_timer():
    global work_timer_started, rest_timer_started, interrupt_timer_thread
    t = time()
    work_timer_started = True
    while (time() - t) < work_time_span:
        print("\rWork time :", round(time()-t, 2), end="")
        sleep(1)
        if interrupt_timer_thread:
            print("\nTime thread interrupted!")
            work_timer_started = False
            interrupt_timer_thread = False
            return
    print()
    work_timer_started = False
    t = time()
    cheat_rest_duration = t - last_activity_detected_on
    rest_timer_started = True
    new_rest_time_span = rest_time_span - cheat_rest_duration
    print("new rest time:::", new_rest_time_span)
    while (time() - t) < new_rest_time_span:
        print("\rRest time :", round(time()-t, 2), end="")
        sleep(1)
        if interrupt_timer_thread:
            print("\nTime thread interrupted!")
            rest_timer_started = False
            interrupt_timer_thread = False
            return
    print()
    rest_timer_started = False


key_listener_thread = key_listener(on_press=detected_activity)
key_listener_thread.start()
with mouse_listener(on_move=detected_activity) as Listener:
    Listener.join()
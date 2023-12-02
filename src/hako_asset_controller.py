#!/usr/bin/python
# -*- coding: utf-8 -*-

from enum import Enum
import time
import hakoc

class HakoAssetController:
    class HakoEvent(Enum):
        NONE = 0
        START = 1
        STOP = 2
        RESET = 3
        ERROR = 4

    class HakoState(Enum):
        STOPPED = 0
        RUNNABLE = 1
        RUNNING = 2
        STOPPING = 3
        RESETTING = 4
        ERROR = 5
        TERMINATED = 6

    def __init__(self, asset_name, delta_usec):
        self.asset_name = asset_name
        self.delta_usec = delta_usec
        self.asset_time_usec = 0

    def initialize(self):
        hakoc.asset_init()
        hakoc.asset_register(self.asset_name)

    def get_asset_time_usec(self):
        return self.asset_time_usec

    def get_world_time_usec(self):
        return hakoc.asset_get_worldtime()

    def usleep(self, sleep_time_usec):
        curr_time = hakoc.asset_get_worldtime()
        target_time = curr_time + sleep_time_usec
        while curr_time < target_time:
            if self.execute_step() == False:
                if self.state() != HakoAssetController.HakoState.RUNNING:
                    break
                else:
                    time.sleep(0.01)
            curr_time = hakoc.asset_get_worldtime()

    def state(self):
        state_value = hakoc.state()
        return HakoAssetController.HakoState(state_value)

    def wait_event(self, ev):
        while True:
            current_ev_value = hakoc.asset_get_event(self.asset_name)
            current_ev = HakoAssetController.HakoEvent(current_ev_value)
            if current_ev == HakoAssetController.HakoEvent.NONE:
                time.sleep(0.01)
            elif current_ev == HakoAssetController.HakoEvent.START:
                hakoc.asset_start_feedback(self.asset_name, True)
                return True
            elif current_ev == HakoAssetController.HakoEvent.STOP:
                hakoc.asset_stop_feedback(self.asset_name, True)
                return True
            elif current_ev == HakoAssetController.HakoEvent.RESET:
                hakoc.asset_reset_feedback(self.asset_name, True)
                self.asset_time_usec = 0
                return True
            else:
                print("ERROR: unknown event:" + str(current_ev))
                return False

    def wait_state(self, expect_state):
        while True:
            if self.state() != expect_state:
                time.sleep(0.01)
            else:
                return True

    def wait_pdu_created(self):
        while True:
            if hakoc.asset_is_pdu_created() == False:
                time.sleep(0.01)
            else:
                return True

    def is_pdu_sync_mode(self):
        return hakoc.asset_is_pdu_sync_mode(self.asset_name)
    
    def execute(self):
        result = hakoc.asset_notify_simtime(self.asset_name, self.asset_time_usec)
        if result == False:
            print("notify_simtime: false")
            return False
        elif self.state() != HakoAssetController.HakoState.RUNNING:
            print("running: false")
            return False
        elif hakoc.asset_is_pdu_created() == False:
            print("pdu_created: false")
            return False
        elif hakoc.asset_is_pdu_sync_mode(self.asset_name) == True:
            print("sync_mode: true")
            return False
        elif hakoc.asset_is_simulation_mode() == False:
            print("simulation mode: false")
            return False
        elif self.asset_time_usec >= hakoc.asset_get_worldtime():
            return False
        else:
            self.asset_time_usec = self.asset_time_usec + self.delta_usec
            return True


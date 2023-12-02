#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import time
from hako_asset_controller import HakoAssetController
from hako_asset_pdu import HakoAssetPdu

class HakoAplRunner:
    def __init__(self, apl, asset_name, robo_name, offset_path, readers, writers):
        self.pdu = HakoAssetPdu(asset_name, robo_name, offset_path)
        self.pdu.create_pdu_lchannel(writers)
        self.pdu.subscribe_pdu_lchannel(readers)
        self.apl = apl
        self.apl.initialize(self.pdu)
    
    def sync_read_pdus(self):
        self.pdu.sync_read_buffers()
    
    def sync_write_pdus(self):
        self.pdu.sync_write_buffers()

    def step(self):
        self.apl.step()

    def reset(self):
        self.apl.reset()


class HakoRunner:
    def __init__(self, filepath):
        with open(filepath, 'r') as file:
            self.config = json.load(file)

        if self.config.get('apl_config_path') != None:
            with open(self.config['apl_config_path'], 'r') as file:
                self.apl_config = json.load(file)
        else:
            self.apl_config = None
        self.controller = HakoAssetController(self.config['asset_name'], self.config['delta_msec'] * 1000)


    def initialize(self, apl):
        self.controller.initialize()

        # ROBOTS FOR APPLICATIONS
        self.apls = []
        if self.apl_config != None:
            for entry in self.apl_config['robots']:
                print("apl:", entry['name'])
                readers = entry['shm_pdu_readers']
                writers = entry['shm_pdu_writers']
                robo = HakoAplRunner(apl, self.controller.asset_name, entry['name'], self.config['offset_path'],readers, writers)
                self.apls.append(robo)


    def apl_sync_write_pdus(self):
        for entry in self.apls:
            entry.sync_write_pdus()

    def apl_sync_read_pdus(self):
        for entry in self.apls:
            entry.sync_read_pdus()

    def apl_step(self):
        for entry in self.apls:
            entry.step()

    def apl_reset(self):
        for entry in self.apls:
            entry.reset()

    def run(self):
        while True:
            print("WAIT START:")
            self.controller.wait_event(HakoAssetController.HakoEvent.START)
            print("WAIT RUNNING:")
            self.controller.wait_state(HakoAssetController.HakoState.RUNNING)
            print("WAIT PDU CREATED:")
            self.controller.wait_pdu_created()

            print("GO:")
            while True:
                if self.controller.execute() == False:
                    if self.controller.state() != HakoAssetController.HakoState.RUNNING:
                        print("WAIT_STOP")
                        self.controller.wait_event(HakoAssetController.HakoEvent.STOP)
                        print("WAIT_RESET")
                        self.controller.wait_event(HakoAssetController.HakoEvent.RESET)
                        self.apl_reset()
                        print("DONE")
                        break
                    else:
                        if self.controller.is_pdu_sync_mode():
                            #FOR APPLS
                            self.apl_sync_write_pdus()
                        continue

                #FOR APLS
                self.apl_sync_read_pdus()
                self.apl_step()
                self.apl_sync_write_pdus()
 
    def _reset(self):
        pass

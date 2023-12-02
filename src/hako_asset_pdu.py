#!/usr/bin/python
# -*- coding: utf-8 -*-

from hako_binary import offset_map
from hako_binary import binary_writer
from hako_binary import binary_reader

import hakoc

class HakoAssetPdu:
    def __init__(self, asset_name, robo_name, offset_path):
        self.asset_name = asset_name
        self.control_asset_name = robo_name
        self.offmap = offset_map.create_offmap(offset_path)

        self.writer_name2channel = {}
        self.writer_channel2type = {}
        self.writer_channel2pdusize = {}

        self.reader_name2channel = {}
        self.reader_channel2type = {}
        self.reader_channel2pdusize = {}

        self.write_raw_buffers = {}
        self.read_raw_buffers = {}

    def create_pdu_lchannel(self, writers):
        if writers == None:
            writers = []
        self.writers = writers
        for writer in writers:
            typename = writer['type'].split('/')[1]
            channel_id = writer['channel_id']
            pdu_size = writer['pdu_size']
            org_name = writer['org_name']
            self.writer_name2channel[org_name] = channel_id
            self.writer_channel2type[channel_id] = typename
            self.writer_channel2pdusize[channel_id] = pdu_size
            print("create:channel_id=" + str(channel_id))
            print("create:typename=" + typename)
            print("create:pdu_size=" + str(pdu_size))
            hakoc.asset_create_pdu_lchannel(self.control_asset_name, channel_id, pdu_size)
            binary_data = bytearray(pdu_size)
            self.write_raw_buffers[channel_id] = binary_data

    def subscribe_pdu_lchannel(self, readers):
        if readers == None:
            readers = []
        self.readers = readers
        for reader in readers:
            channel_id = reader['channel_id']
            pdu_size = reader['pdu_size']
            org_name = reader['org_name']
            typename = reader['type'].split('/')[1]
            self.reader_name2channel[org_name] = channel_id
            self.reader_channel2type[channel_id] = typename
            self.reader_channel2pdusize[channel_id] = pdu_size
            print("subscribe:channel_id=" + str(channel_id))
            print("subscribe:typename=" + typename)
            print("subscribe:pdu_size=" + str(pdu_size))
            binary_data = bytearray(pdu_size)
            self.read_raw_buffers[channel_id] = binary_data

    def _read_pdu(self, channel_id):
        hakoc.asset_read_pdu(self.asset_name, 
                             self.control_asset_name, 
                             channel_id, 
                             self.read_raw_buffers[channel_id], 
                             self.reader_channel2pdusize[channel_id])

    def sync_read_buffers(self):
        for reader in self.readers:
            channel_id = reader['channel_id']
            self._read_pdu(channel_id)

    def get_read_pdu_json(self, channel_id):
        typename = self.reader_channel2type[channel_id]
        binary_data = self.read_raw_buffers[channel_id]
        return binary_reader.binary_read(self.offmap, typename, binary_data)
    
    def update_write_buffer(self, channel_id, pdu_json):
        typename = self.writer_channel2type[channel_id]
        #print(json.dumps(pdu_json))
        binary_data = self.write_raw_buffers[channel_id]
        binary_writer.binary_write(self.offmap, binary_data, pdu_json, typename)

    def get_write_pdu_json(self, channel_id):
        typename = self.writer_channel2type[channel_id]
        binary_data = self.write_raw_buffers[channel_id]
        return binary_reader.binary_read(self.offmap, typename, binary_data)

    def sync_write_buffers(self):
        for writer in self.writers:
            channel_id = writer['channel_id']
            hakoc.asset_write_pdu(self.asset_name, self.control_asset_name, channel_id, self.write_raw_buffers[channel_id], self.writer_channel2pdusize[channel_id])
            hakoc.asset_notify_write_pdu_done(self.asset_name)

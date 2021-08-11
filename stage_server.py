#!/usr/bin/python3
# stage_server.py
# 7/6/2020
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# This a server for the 3 Standa stages R, Theta, Z

from astropy.io import fits
from ctypes import *
import numpy as np
import asyncio
import logging
import os
import sys
import time
import math
import threading

#### Steps<->mm/deg/mm Conversion ####################
R_CONST = 0.025 # mm
T_CONST = 0.144 # deg
Z_CONST = 0.00125 # mm
######################################################

#### Home Offsets (steps) ############################
R_HOME_DELTA = int(340)
R_HOME_U_DELTA = int(190)

T_HOME_DELTA = int(-8) 
T_HOME_U_DELTA = int(-227)

Z_HOME_DELTA = int(10590)
Z_HOME_U_DELTA = int(0)
######################################################

#### Soft Stops ######################################
R_SOFT_STOP_R = 340 #305.5
R_SOFT_STOP_L = 0 #0
T_SOFT_STOP_R = 180 #180
T_SOFT_STOP_L = -180 #-180
Z_SOFT_STOP_R = 12.5 #12.5
Z_SOFT_STOP_L = -12.5 #-12.5
######################################################

def log_start():
    """
    Create a logfile that the rest of the script can write to.

    Output:
    - log 	Object used to access write abilities
    """

    scriptDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scriptName = os.path.splitext(os.path.basename(__file__))[0]
    log = logging.getLogger('stage_server')
    hdlr = logging.FileHandler(scriptDir+'/logs/'+scriptName+'.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    log.setLevel(logging.INFO)
    return log

def scan_for_devices():
    """
    Scans for motor controllers on USB

    Returns the number and list of devices found
    """

    probe_flags = EnumerateFlags.ENUMERATE_PROBE
    devenum = lib.enumerate_devices(probe_flags, None)
    dev_count = lib.get_device_count(devenum)
    controller_name = controller_name_t()

    devices_list = []
    for dev_ind in range(0, dev_count):
        enum_name = lib.get_device_name(devenum, dev_ind)
        result = lib.get_enumerate_device_controller_name(devenum, dev_ind, byref(controller_name))

        if result == Result.Ok:
            devices_list.append(enum_name)

    return devices_list, dev_count

def get_move_status(lib, device_id):
    """
    Returns the moving status of the given device

    Inputs:
    - lib       The library for accessing these devices
    - device_id The ID of the desired device

    Output:
    - BUSY/IDLE
    """

    device_status = status_t()

    result = lib.get_status(device_id, byref(device_status))
    if result == Result.Ok:
        move_com_state = device_status.MvCmdSts

        if move_com_state == 129:
            return 'BUSY'
        else:
            return 'IDLE'

def get_status(lib, open_devs):
    """
    Returns the full status of all connected devices.

    Inputs:
    - lib       The library for accessing these devices
    - open_devs The list of all connected devices

    Output:
    - response      OK/BAD
    - all_status    A string containing info on all devices
    """

    all_status = ''
    r_status = status_t()
    t_status = status_t()
    z_status = status_t()

    r_result = lib.get_status(open_devs[0], byref(r_status))
    t_result = lib.get_status(open_devs[1], byref(t_status))
    z_result = lib.get_status(open_devs[2], byref(z_status))

    if r_result == Result.Ok and t_result == Result.Ok and z_result == Result.Ok:
        response, all_pos = get_position(lib, open_devs)
        r_speed, r_uspeed = get_speed(lib, open_devs[0])
        t_speed, t_uspeed = get_speed(lib, open_devs[1])
        z_speed, z_uspeed = get_speed(lib, open_devs[2])

        r_speed = R_CONST*(r_speed + (r_uspeed/256))
        t_speed = T_CONST*(t_speed + (t_uspeed/256))
        z_speed = Z_CONST*(z_speed + (z_uspeed/256))

        r_move_state = get_move_status(lib, open_devs[0])
        t_move_state = get_move_status(lib, open_devs[1])
        z_move_state = get_move_status(lib, open_devs[2])

        if response == 'OK':
            all_status = "\nr = "+str(round(all_pos[0][0],4))+" mm "+r_move_state+"\
                        \n\u03B8 = "+str(round(all_pos[1][0],4))+" deg "+t_move_state+"\
                        \nz = "+str(round(all_pos[2][0],4))+" mm "+z_move_state+"\
                        \n\
                        \nr_e = "+str(all_pos[0][1])+"\
                        \n\u03B8_e = "+str(all_pos[1][1])+"\
                        \nz_e = "+str(all_pos[2][1])+"\
                        \n\
                        \nr_s = "+str(round(r_speed,4))+" mm/s"+"\
                        \n\u03B8_s = "+str(round(t_speed,4))+" deg/s"+"\
                        \nz_s = "+str(round(z_speed,4))+" mm/s"
    else:
        response = 'BAD: get_status() failed'
    return response, all_status

def get_position(lib, open_devs):
    """
    Returns the positions of all the connected devices

    Inputs:
    - lib       The library for accessing these devices
    - open_devs The list of all connected devices

    Output:
    - response  OK/BAD
    - all_pos   list of all positions in standard units and encoder counts
    """

    response = 'OK'
    r_pos = get_position_t()
    t_pos = get_position_t()
    z_pos = get_position_t()

    r_result = lib.get_position(open_devs[0], byref(r_pos))
    t_result = lib.get_position(open_devs[1], byref(t_pos))
    z_result = lib.get_position(open_devs[2], byref(z_pos))

    all_pos = []

    if r_result == Result.Ok and t_result == Result.Ok and z_result == Result.Ok:
        # Convert the position from steps to readable units (as specified at beginning of script)
        r_pos_mm = R_CONST*(r_pos.Position + (r_pos.uPosition / 256))
        t_pos_am = T_CONST*(t_pos.Position + (t_pos.uPosition / 256))
        z_pos_mm = Z_CONST*(z_pos.Position + (z_pos.uPosition / 256))

        r_pos_enc = r_pos.EncPosition
        t_pos_enc = -1 * t_pos.EncPosition
        z_pos_enc = z_pos.EncPosition

        all_pos = [[r_pos_mm, r_pos_enc], [t_pos_am, t_pos_enc], [z_pos_mm, z_pos_enc]]
    else:
        response = 'BAD: get_position() failed'
    return response, all_pos

def get_step_position(lib, device_id):
    """
    Returns the position in steps. Microsteps (#/256) converted
    to decimal.

    Inputs:
    - lib       The library for accessing these devices
    - device_id The ID of the desired device

    Output:
    - position  The step count as a decimal
    """

    response = 'OK'
    device_pos = get_position_t()

    result = lib.get_position(device_id, byref(device_pos))
    if result == Result.Ok:
        position = device_pos.Position + (device_pos.uPosition / 256)
    else:
        response = 'BAD: get_position() failed'
    return position

def get_speed(lib, device_id):
    """
    Returns the speed in steps/s.

    Inputs:
    - lib       The library for accessing these devices
    - device_id The ID of the desired device

    Output:
    - mvst.Speed    Speed in steps
    - mvst.uSpeed   Leftover uSteps
    """

    mvst = move_settings_t()
    result = lib.get_move_settings(device_id, byref(mvst))
    if result == Result.Ok:    
        return mvst.Speed, mvst.uSpeed
    else:
        return 0

def set_speed(lib, device_id, speed):
    """
    Sets the speed in steps/s.

    Inputs:
    - lib       The library for accessing these devices
    - device_id The ID of the desired device
    - speed     Speed (as a decimal) in steps/s

    Output:
    - OK/BAD
    """

    mvst = move_settings_t()
    result = lib.get_move_settings(device_id, byref(mvst))

    if result == Result.Ok:
        # split the integer from the decimal
        u_speed, speed = math.modf(speed)

        # convert the decimal to #/256
        u_speed = u_speed * 256

        # prepare move_settings_t struct
        mvst.Speed = int(speed)
        mvst.uSpeed = int(u_speed)
        result = lib.set_move_settings(device_id, byref(mvst))
        if result == Result.Ok:
            return 'OK'
        else:
            return 'BAD: set_move_settings() failed'
    else:
        return 'BAD: get_move_settings() failed'

def move(lib, device_id, distance):
    """
    Sends a move command for the given steps.

    Inputs:
    - lib       The library for accessing these devices
    - device_id The ID of the desired device
    - distance  In steps as a decimal

    Output:
    - OK/BAD
    """

    # split the integer from the decimal
    u_distance, distance = math.modf(distance)

    # convert the decimal to #/256
    u_distance = u_distance * 256

    result = lib.command_move(device_id, int(distance), int(u_distance))
    if result == Result.Ok:
        return 'OK'
    else:
        return 'BAD: Move command failed'

def home(lib, device_id):
    """
    Sends a home command for the given device.

    Inputs:
    - lib       The library for accessing these devices
    - device_id The ID of the desired device

    Output:
    - OK/BAD
    """
    result = lib.command_homezero(device_id)
    print('done homing')
    if result == Result.Ok:
        return 'OK'
    else:
        return 'BAD: Home command failed'

def soft_stop(lib, device_id):
    """
    Sends a stop command to the given device.

    Inputs:
    - lib       The library for accessing these devices
    - device_id The ID of the desired device

    Output:
    - OK/BAD
    """
    result = lib.command_sstp(device_id)
    if result == Result.Ok:
        return 'OK'
    else:
        return 'BAD: Soft stop failed'

def set_zero(lib, device_id):
    """
    Sets the current position to zero for the given device. 
    Both step counts and encoder counts are zeroed.

    Inputs:
    - lib       The library for accessing these devices
    - device_id The ID of the desired device

    Output:
    - OK/BAD
    """
    result = lib.command_zero(device_id)
    if result == Result.Ok:
        return 'OK'
    else:
        return 'BAD: Zeroing failed'

# command handler, to parse the client's data more precisely
def handle_command(log, writer, data): 
    """
    Determines what to do with the incoming data, whether it is move, offset,
    home, or set speed. This is a separate method from handle_client() 
    because it is called as a new thread, so ensure the exposure is non-blocking.

    Input:
    - log       object to access the logger
    - writer    object to write data back to the client
    - data      the data received from the client
    """

    response = ''
    response_r = ''
    response_t = ''
    response_z = ''

    commandList = data.split()
    
    try:
        # Move desired axes to absolute position, given in desired units
        if commandList[0] == 'move' and len(commandList) > 1:
            # send move commands for each axis given
            for axis in commandList[1:]:
                if axis[:2] == 'r=' and get_move_status(lib, open_devs[0]) == 'IDLE':
                    try:
                        # move r axis
                        r_move_temp = float(axis[2:])
                        if r_move_temp >= R_SOFT_STOP_L and r_move_temp <= R_SOFT_STOP_R:
                            r_move = r_move_temp / R_CONST
                            response_r = move(lib, open_devs[0], r_move)
                        else:
                            response_r = 'BAD: Outside of limits'

                    except ValueError:
                        response_r = 'BAD: Invalid move'

                elif axis[:2] == 't=' and get_move_status(lib, open_devs[1]) == 'IDLE':
                    try:
                        # move theta axis
                        t_move_temp = float(axis[2:])
                        if t_move_temp >= T_SOFT_STOP_L and t_move_temp <= T_SOFT_STOP_R:
                            t_move = t_move_temp / T_CONST
                            response_t = move(lib, open_devs[1], t_move)
                        else:
                            response_t = 'BAD: Outside of limits'
                        
                    except ValueError:
                        response_t = 'BAD: Invalid move'

                elif axis[:2] == 'z=' and get_move_status(lib, open_devs[2]) == 'IDLE':
                    try:
                        # move z axis
                        z_move_temp = float(axis[2:])
                        if z_move_temp >= Z_SOFT_STOP_L and z_move_temp <= Z_SOFT_STOP_R:
                            z_move = z_move_temp / Z_CONST
                            response_z = move(lib, open_devs[2], z_move)
                        else:
                            response_z = 'BAD: Outside of limits'

                    except ValueError:
                        response_z = 'BAD: Invalid move'

                else:
                    response = 'BAD: Invalid move' 

        # Offset desired axes from current position
        elif commandList[0] == 'offset' and len(commandList) > 1:
            # send offset commands for each axis given
            for axis in commandList[1:]:
                if axis[:2] == 'r=' and get_move_status(lib, open_devs[0]) == 'IDLE':
                    try:
                        # offset r axis
                        r_cur_position = get_step_position(lib, open_devs[0])
                        r_cur_position_temp = r_cur_position * R_CONST
                        r_offset_temp = float(axis[2:])
                        #print('DEBUG: '+ repr(r_cur_position_temp + r_offset_temp))
                        if (r_cur_position_temp + r_offset_temp) >= R_SOFT_STOP_L and (r_cur_position_temp + r_offset_temp) <= R_SOFT_STOP_R: 
                            r_offset = r_offset_temp / R_CONST
                            response_r = move(lib, open_devs[0], r_cur_position + r_offset)
                        else:
                            response_r = 'BAD: Outside of limits'

                    except ValueError:
                        response_r = 'BAD: Invalid offset'

                elif axis[:2] == 't=' and get_move_status(lib, open_devs[1]) == 'IDLE':
                    try:
                        # offset theta axis
                        t_cur_position = get_step_position(lib, open_devs[1])
                        t_cur_position_temp = t_cur_position * T_CONST
                        t_offset_temp = float(axis[2:])
                        
                        if (t_cur_position_temp + t_offset_temp) >= T_SOFT_STOP_L and (t_cur_position_temp + t_offset_temp) <= T_SOFT_STOP_R: 
                            t_offset = t_offset_temp / T_CONST
                            response_t = move(lib, open_devs[1], t_cur_position + t_offset)
                        else:
                            response_t = 'BAD: Outside of limits'
                        
                    except ValueError:
                        response_t = 'BAD: Invalid offset'

                elif axis[:2] == 'z=' and get_move_status(lib, open_devs[2]) == 'IDLE':
                    try:
                        # offset z axis
                        z_cur_position = get_step_position(lib, open_devs[2])
                        z_cur_position_temp = z_cur_position * Z_CONST
                        z_offset_temp = float(axis[2:])
                        
                        if (z_cur_position_temp + z_offset_temp) >= Z_SOFT_STOP_L and (z_cur_position_temp + z_offset_temp) <= Z_SOFT_STOP_R: 
                            z_offset = z_offset_temp / Z_CONST
                            response_z = move(lib, open_devs[2], z_cur_position + z_offset)
                        else:
                            response_z = 'BAD: Outside of limits'

                    except ValueError:
                        response_z = 'BAD: Invalid offset'

                else:
                    response = 'BAD: Invalid offset'            

        # Home desired stages
        elif commandList[0] == 'home' and len(commandList) >= 2:
            # home given axes or all axes if len(commandList) == 1 
            for axis in commandList[1:]:
                if axis[:2] == 'r' and get_move_status(lib, open_devs[0]) == 'IDLE':
                    hmst = home_settings_t()
                    result = lib.get_home_settings(open_devs[0], byref(hmst))
                    
                    if result == Result.Ok:
                        # Set all Homing Settings
                        hmst.FastHome = int(100)
                        hmst.uFastHome = int(0)
                        hmst.SlowHome = int(100)
                        hmst.uSlowHome = int(0)
                        hmst.HomeDelta = R_HOME_DELTA
                        hmst.uHomeDelta = R_HOME_U_DELTA
                        hmst.HomeFlags = int(370)
                        result2 = lib.set_home_settings(open_devs[0], byref(hmst))
                        
                        if result2 == Result.Ok:
                            response = home(lib, open_devs[0])
                        else:
                            return 'BAD: set_home_settings() failed'
                    else:
                        response = 'BAD: get_home_settings() failed'

                elif axis[:2] == 't' and get_move_status(lib, open_devs[1]) == 'IDLE':
                    t_cur_position = get_step_position(lib, open_devs[1])
                    # theta limit switch is close to zero, so move +100steps from zero before homing
                    if t_cur_position <= 100:
                        move(lib, open_devs[1], 100)
                        time.sleep(1)

                        # don't send home command until stage is done moving
                        while get_move_status(lib, open_devs[1]) == 'BUSY':
                            time.sleep(0.1)

                    # home immediately if stage is in good position
                    hmst = home_settings_t()
                    result = lib.get_home_settings(open_devs[1], byref(hmst))

                    if result == Result.Ok:
                        # Set all Homing settings
                        hmst.FastHome = int(20)
                        hmst.uFastHome = int(0)
                        hmst.SlowHome = int(20)
                        hmst.uSlowHome = int(0)
                        hmst.HomeDelta = T_HOME_DELTA
                        hmst.uHomeDelta = T_HOME_U_DELTA
                        hmst.HomeFlags = int(114)

                        result = lib.set_home_settings(open_devs[1], byref(hmst))
                        
                        if result == Result.Ok:
                            response = home(lib, open_devs[1])
                        else:
                            return 'BAD: set_home_settings() failed'
                    else:
                        response = 'BAD: get_home_settings() failed'

                elif axis[:2] == 'z' and get_move_status(lib, open_devs[2]) == 'IDLE':
                    hmst = home_settings_t()
                    result = lib.get_home_settings(open_devs[2], byref(hmst))

                    if result == Result.Ok:
                        # Set all Homing settings
                        hmst.FastHome = int(500)
                        hmst.uFastHome = int(0)
                        hmst.SlowHome = int(500)
                        hmst.uSlowHome = int(0)
                        hmst.HomeDelta = Z_HOME_DELTA
                        hmst.uHomeDelta = Z_HOME_U_DELTA
                        hmst.HomeFlags = int(370)

                        result = lib.set_home_settings(open_devs[2], byref(hmst))
                        
                        if result == Result.Ok:
                            response = home(lib, open_devs[2])
                        else:
                            return 'BAD: set_home_settings() failed'
                    else:
                        response = 'BAD: get_home_settings() failed'

                else:
                    response = 'BAD: home failed' 

        # Home all stages at once
        elif commandList[0] == 'home' and len(commandList) == 1:
            if get_move_status(lib, open_devs[0]) == 'IDLE':
                hmst = home_settings_t()
                result = lib.get_home_settings(open_devs[0], byref(hmst))
                
                if result == Result.Ok:
                    # Set all Homing Settings
                    hmst.FastHome = int(100)
                    hmst.uFastHome = int(0)
                    hmst.SlowHome = int(100)
                    hmst.uSlowHome = int(0)
                    hmst.HomeDelta = R_HOME_DELTA
                    hmst.uHomeDelta = R_HOME_U_DELTA
                    hmst.HomeFlags = int(370)
                    result2 = lib.set_home_settings(open_devs[0], byref(hmst))
                    
                    if result2 == Result.Ok:
                        response = home(lib, open_devs[0])
                    else:
                        return 'BAD: set_home_settings() failed'
                else:
                    response = 'BAD: get_home_settings() failed'
            else:
                response_r = 'BAD: r home failed, BUSY'

            if get_move_status(lib, open_devs[1]) == 'IDLE':
                t_cur_position = get_step_position(lib, open_devs[1])

                # theta limit switch is close to zero, so move +100steps from zero before homing
                if t_cur_position <= 100:
                    move(lib, open_devs[1], 100)
                    time.sleep(1)

                    # don't send home command until stage is done moving
                    while get_move_status(lib, open_devs[1]) == 'BUSY':
                        time.sleep(0.1)

                # home immediately if stage is in good position
                hmst = home_settings_t()
                result = lib.get_home_settings(open_devs[1], byref(hmst))

                if result == Result.Ok:
                    # Set all Homing settings
                    hmst.FastHome = int(20)
                    hmst.uFastHome = int(0)
                    hmst.SlowHome = int(20)
                    hmst.uSlowHome = int(0)
                    hmst.HomeDelta = T_HOME_DELTA
                    hmst.uHomeDelta = T_HOME_U_DELTA
                    hmst.HomeFlags = int(114)

                    result = lib.set_home_settings(open_devs[1], byref(hmst))
                    
                    if result == Result.Ok:
                        response = home(lib, open_devs[1])
                    else:
                        return 'BAD: set_home_settings() failed'
                else:
                    response = 'BAD: get_home_settings() failed'

            else:
                response_t = 'BAD: theta home failed'

            if get_move_status(lib, open_devs[2]) == 'IDLE':
                hmst = home_settings_t()
                result = lib.get_home_settings(open_devs[2], byref(hmst))

                if result == Result.Ok:
                    # Set all Homing settings
                    hmst.FastHome = int(500)
                    hmst.uFastHome = int(0)
                    hmst.SlowHome = int(500)
                    hmst.uSlowHome = int(0)
                    hmst.HomeDelta = Z_HOME_DELTA
                    hmst.uHomeDelta = Z_HOME_U_DELTA
                    hmst.HomeFlags = int(370)

                    result = lib.set_home_settings(open_devs[2], byref(hmst))
                    
                    if result == Result.Ok:
                        response = home(lib, open_devs[2])
                    else:
                        return 'BAD: set_home_settings() failed'
                else:
                    response = 'BAD: get_home_settings() failed'
            else:
                response_z = 'BAD: z home failed'

            response = response_r + response_t + response_z
            if 'BAD' in response:
                response = 'BAD: Homing failed'
            else:
                response = 'OK'

        # Set the speed
        elif commandList[0] == 'speed' and len(commandList) > 1:
            # set the given axes to the given speeds
            #print('...Setting speeds...')
            for axis in commandList[1:]:
                if axis[:2] == 'r=':
                    try:
                        # set r axis speed
                        r_set_speed = float(axis[2:]) / R_CONST
                        response_r = set_speed(lib, open_devs[0], r_set_speed)

                    except ValueError:
                        response_r = 'BAD: Invalid speed'

                elif axis[:2] == 't=':
                    try:
                        # set theta axis speed
                        t_set_speed = float(axis[2:]) / T_CONST
                        response_t = set_speed(lib, open_devs[1], t_set_speed)
                        
                    except ValueError:
                        response_t = 'BAD: Invalid speed'

                elif axis[:2] == 'z=':
                    try:
                        # set z axis speed
                        z_set_speed = float(axis[2:]) / Z_CONST
                        response_z = set_speed(lib, open_devs[2], z_set_speed)

                    except ValueError:
                        response_z = 'BAD: Invalid speed'

                else:
                    response = 'BAD: Invalid set speed command' 
        
        # set zero
        elif commandList[0] == 'zero' and len(commandList) > 1:
            # set the given axes to zero
            for axis in commandList[1:]:
                if axis[:2] == 'r':
                    try:
                        response_r = set_zero(lib, open_devs[0])
                    except:
                        response_r = 'BAD: Zero R failed'
                
                elif axis[:2] == 't':
                    try:
                        response_t = set_zero(lib, open_devs[1])
                    except:
                        response_t = 'BAD: Zero T failed'

                elif axis[:2] == 'z':
                    try:
                        response_z = set_zero(lib, open_devs[2])
                    except:
                        response_z = 'BAD: Zero Z failed'
                else:
                    response = 'BAD: Invalid axis to zero'
        else:
            response = 'BAD: Invalid Command'

        response = response_r + response_t + response_z
        if 'BAD' in response:
            response = 'BAD'
        else:
            response = 'OK'

    except IndexError:
        response = 'BAD: Invalid Command'
    
    #log.info('RESPONSE = '+response)
    writer.write((response+'\n').encode('utf-8'))
    # wait for all activity to cease. handle_command() is called as a new thread
    # so this will not cause blocking 
    time.sleep(1.5)
    while get_move_status(lib, open_devs[0]) == 'BUSY' \
        or get_move_status(lib, open_devs[1]) == 'BUSY' \
        or get_move_status(lib, open_devs[2]) == 'BUSY':
        
        time.sleep(0.1)

    # tell the client the result of their command & log it
    #log.info('RESPONSE = DONE')
    writer.write(('DONE\n').encode('utf-8'))

# async client handler, for multiple connections
async def handle_client(reader, writer):
    """
    This is the method that receives the client's data and decides what to do
    with it. It runs in a loop to always be accepting new connections. If the
    data is 'status', all motor status are returned. If the data is 'stop', all
    running motors are stopped and set to ready state. If anything else, a new 
    thread is created and the data is sent to handle_command().

    Inputs:
    - reader    from the asyncio library, to read incoming data
    - writer    from the asyncio library, to write outgoing data
    """

    request = None
    while request != 'quit':        
        request = (await reader.read(255)).decode('utf8').strip()
        print(request.encode('utf8'))
        #log.info('COMMAND: '+request)
        writer.write(('COMMAND: '+request.upper()+'\n').encode('utf8'))    

        response = 'BAD'
        # check if data is empty, a status query, or potential command
        dataDec = request
        if dataDec == '':
            break
        elif 'status' in dataDec.lower():
            busyState = 'IDLE'

            # check if any of the stages are moving
            for each in open_devs:
                if get_move_status(lib, each) == 'BUSY':
                    busyState = 'BUSY'

            response, all_status = get_status(lib, open_devs)
            response = response + '\n' + busyState + '\n' + all_status

            # send current status to open connection & log it
            #log.info('RESPONSE = '+response)
            writer.write((response+'\nDONE\n').encode('utf-8'))
            
        elif 'stop' in dataDec.lower():
            busyState = 'IDLE'
            stopList =[]

            # check if any of the stages are moving
            for each in open_devs:
                if get_move_status(lib, each) == 'BUSY':
                    busyState = 'BUSY'
                    stopList.append(each)

            if len(stopList) != 0:
                response = ''
                for each in stopList:
                    response = response + soft_stop(lib, each)

                if 'BAD' in response:
                    response = 'BAD: Stop failed'
                else:
                    response = 'OK: Move Aborted'

            else:
                response = 'OK: All stages IDLE'

            # send current status to open connection & log it
            #log.info('RESPONSE = '+response)
            writer.write((response+'\nDONE\n').encode('utf-8'))

        else:
            # handler for all other commands besides status & stop
            comThread = threading.Thread(target=handle_command, args=(log, writer, dataDec,))
            comThread.start()

        await writer.drain()
    writer.close()

async def main(HOST, PORT):
    print("Opening connection @"+HOST+":"+str(PORT))
    server = await asyncio.start_server(handle_client, HOST, PORT)
    await server.serve_forever()

if __name__ == "__main__":

    # Check if Python version is >= 3.0
    if sys.version_info >= (3,0):
        import urllib.parse

    # Set the current directory and get the path to pyximc.py
    cur_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    ximc_dir = ("/gitrepos/sdss-v-fsc/ximc-2.12.1/ximc")
    ximc_package_dir = os.path.join(ximc_dir, "crossplatform", "wrappers", "python")
    sys.path.append(ximc_package_dir)

    try: 
        from pyximc import *
    except ImportError as err:
        print ("Can't import pyximc module. The most probable reason is that you changed the relative location of the files..")
        exit()

    dev_list, dev_count = scan_for_devices()
    open_devs = ['','','']

    print("Number of devices: "+str(dev_count))
    try:
        #print("List of devices:")
        all_device_check = True
        for i in dev_list:
            #print(repr(i))

            if '49E5' in repr(i):
                axis_r = lib.open_device(i)
                #print('r id: ' + repr(axis_r))
                if axis_r > 0:
                    open_devs[0] = axis_r
                else:
                    all_device_check = False
                    #print('BAD, R stage connection failed')

            elif '3F53' in repr(i):
                axis_t = lib.open_device(i)
                #print('\u03B8 id: ' + repr(axis_t))
                if axis_t > 0:
                    open_devs[1] = axis_t
                else:
                    all_device_check = False
                    #print('BAD, Theta stage connection failed')

            elif '49F3' in repr(i):
                axis_z = lib.open_device(i)
                #print('z id: ' + repr(axis_z))
                if axis_z > 0:
                    open_devs[2] = axis_z
                else:
                    all_device_check = False
                    #print('BAD, Z stage connection failed')

        if all_device_check:
            # for i in open_devs:
            #     print(repr(i))

            fileDir = os.path.expanduser('~')+'/Pictures/'
            log = log_start()

            # setup Remote TCP Server
            HOST, PORT = '', 9997

            try:
                asyncio.run(main(HOST,PORT))
            except KeyboardInterrupt:
                print('\n...Closing server...')
                for n in open_devs:
                    lib.close_device(byref(cast(n, POINTER(c_int))))
                print('Done')
            except:
                print('Unknown error')

    except IndexError:
        print("No devices to list...")

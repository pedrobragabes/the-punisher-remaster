"""Experimental layout contract for the 1280x960 preset at 1080p/1440p.

Coordinates are pixels in the observed PC UI path, not a blanket 2x transform.
The existing widescreen hook can still reposition individual widgets at runtime.
"""
import re
import struct
import pefile
from punisher_lab import digest

EXPECTED_EXE = 'de995c66c7388532942264aa2d9455ac5d10e254d0713aeacd3ea0690098878a'
ROW_HEIGHT = 36
# Instruction addresses, original row heights, and calls to the list constructor.
ROWS = {
    'ig_menu_list': (0x5ec735, 20, 0x5ec75c),
    'ap_action_list': (0x5ed603, 20, 0x5ed62a),
    'av_setting_list': (0x5eddc5, 20, 0x5eddec),
    'av_value_list': (0x5edec5, 20, 0x5edeec),
    'bf_action_list': (0x5ee1f2, 20, 0x5ee219),
    'ch_selection_list': (0x5ee92c, 20, 0x5ee953),
    'ch_value_list': (0x5eeb55, 20, 0x5eeb7c),
    'ex_action_list': (0x5ef09c, 20, 0x5ef0c6),
    'gs_setting_list': (0x5ef705, 20, 0x5ef72c),
    'gs_value_list': (0x5ef915, 20, 0x5ef93c),
    'wj_action_list': (0x5efb1c, 20, 0x5efb49),
    'mv_action_list': (0x5efe4c, 20, 0x5efe76),
    'op_action_list': (0x5f029c, 20, 0x5f02c6),
    'pc_command_1': (0x5f06dc, 20, 0x5f0703),
    'pc_key_1_A': (0x5f078c, 20, 0x5f07b3),
    'pc_key_1_B': (0x5f083c, 20, 0x5f0863),
    'pc_command_2': (0x5f0adc, 20, 0x5f0b03),
    'pc_key_2_A': (0x5f0b8c, 20, 0x5f0bb3),
    'pc_key_2_B': (0x5f0c3c, 20, 0x5f0c63),
    'pc_toggle_list': (0x5f0d35, 20, 0x5f0d5c),
    'pc_value_list': (0x5f0e45, 20, 0x5f0e6c),
    'pc_setting': (0x5f0f15, 20, 0x5f0f3c),
    'pc_setting_value': (0x5f0fb5, 20, 0x5f0fdc),
    'pf_gui_list': (0x5f118c, 20, 0x5f11b6),
    'pf_select_list': (0x5f13ac, 20, 0x5f13dc),
    'tr_action_list': (0x5f166c, 20, 0x5f1696),
    'ug_selection_list': (0x5f1b05, 20, 0x5f1b32),
    'ug_level_list': (0x5f1ba5, 20, 0x5f1bd2),
    'ug_score_list': (0x5f1c3c, 20, 0x5f1c69),
    'wz_level_list': (0x5f210c, 18, 0x5f2133),
}

LAYOUT = {
    'ap_action_bg': (30, 92, 430, 310), 'ap_action_list': (60, 100, 380, 288),
    'ig_menu_bg': (30, 92, 490, 202), 'ig_menu_list': (50, 100, 450, 180),
    'wz_level_bg': (30, 92, 710, 604), 'wz_level_list': (50, 100, 660, 576),
    'wz_miss_name_text': (50, 710, 660, 36), 'wz_miss_desc_text': (50, 754, 660, 144),
    'wz_high_score_text': (820, 710, 330, 36), 'wz_high_score': (1180, 710, 260, 36),
    'wz_medal_text': (820, 764, 330, 36), 'wz_medal_bmp': (1180, 754, -1, -1),
    'pf_gui_list': (50, 100, 450, 540), 'pf_select_list': (540, 100, 800, 540),
    'op_menu_bg': (30, 92, 530, 130), 'op_action_list': (50, 100, 490, 108),
    'pc_controls_menu_bg': (20, 92, 1780, 694),
    'pc_command_1': (40, 110, 460, 540), 'pc_key_1_A': (520, 110, 160, 540),
    'pc_key_1_B': (700, 110, 160, 540), 'pc_command_2': (920, 110, 460, 540),
    'pc_key_2_A': (1400, 110, 160, 540), 'pc_key_2_B': (1580, 110, 180, 540),
    'pc_toggle_list': (40, 688, 500, 72), 'pc_value_list': (560, 688, 280, 72),
    'pc_setting': (920, 688, 520, 36), 'pc_setting_value': (1460, 688, 260, 36),
    'gs_menu_bg': (30, 112, 1120, 310),
    'gs_setting_list': (50, 120, 740, 288), 'gs_value_list': (810, 120, 310, 288),
    'av_menu_bg': (30, 112, 1120, 202),
    'av_setting_list': (50, 120, 740, 180), 'av_value_list': (810, 120, 310, 180),
    # Original 320x240 Bink reaches at most 1280x720 at the target resolutions.
    # Keep its native-size sentinel; the engine overwrites explicit table sizes.
    'bf_action_list': (50, 110, 500, 216), 'bf_movie': (600, 110, -1, -1),
    'bf_detail_bg': (30, 350, 530, 470), 'bf_heading_text': (58, 370, 480, 36),
    'bf_obj_1': (58, 420, 480, 108), 'bf_obj_2': (58, 548, 480, 108),
    'bf_obj_3': (58, 676, 480, 108), 'bf_challenge': (58, 420, 480, 364),
    'bf_rifle': (80, 440, -1, -1), 'bf_l_pistol': (80, 560, -1, -1),
    'bf_r_pistol': (80, 680, -1, -1), 'bf_briefing_text': (600, 850, 1180, 180),
    'ug_selection_list': (50, 160, 640, 432),
    'ug_level_list': (720, 160, 150, 432), 'ug_score_list': (910, 160, 240, 432),
    'ug_points_bg': (30, 85, 1120, 56), 'ug_unspend_text': (60, 96, 1060, 36),
    'ug_unspend_box': (1160, 160, 600, 180), 'ug_description': (60, 640, 1100, 144),
    'ay_name': (50, 70, 1180, 36), 'ay_desc': (50, 114, 1180, 144),
    'ay_box': (1180, 300, 500, 180),
    'wj_menu_bg': (30, 92, 660, 94), 'wj_action_list': (60, 100, 610, 72),
    'cc_name': (50, 70, 1180, 36), 'cc_desc': (50, 114, 1180, 144),
    'nc_name': (50, 70, 1180, 144),
    'ex_menu_bg': (30, 92, 660, 274), 'ex_action_list': (50, 100, 620, 252),
    'mv_menu_bg': (30, 92, 880, 202), 'mv_action_list': (50, 100, 840, 180),
    'tr_menu_bg': (30, 92, 880, 202), 'tr_action_list': (50, 100, 840, 180),
    'ch_menu_bg': (30, 92, 1000, 670),
    'ch_selection_list': (50, 100, 700, 648), 'ch_value_list': (780, 100, 220, 648),
    'start_text': (490, 800, 420, 36), 'exit_text': (490, 850, 420, 36),
}

PATTERN = re.compile(r'(\$Name:\s*"([^"]+)"\s+)(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)([^\r\n]*)(\r?\n)?$')


def patch_layout(data):
    section = None
    seen = set()
    result, changes = [], []
    for line in data.decode('ascii').splitlines(keepends=True):
        if line.startswith('#'):
            section = line.strip()[1:]
        match = PATTERN.match(line)
        if section == '1280x960' and match and match[2] in LAYOUT:
            name = match[2]
            if name in seen:
                raise ValueError(f'Duplicate layout: {name}')
            seen.add(name)
            changes.append(dict(name=name, before=[int(match[i]) for i in range(3, 7)], after=LAYOUT[name]))
            line = match[1] + '\t'.join(map(str, LAYOUT[name])) + match[7] + (match[8] or '')
        result.append(line)
    if seen != LAYOUT.keys():
        raise ValueError(f'Missing layout entries: {LAYOUT.keys() - seen}')
    return ''.join(result).encode('ascii'), changes


def patch_rows(original):
    if digest(original) != EXPECTED_EXE:
        raise ValueError('Unsupported executable; row patches require the known original hash')
    pe = pefile.PE(data=original)
    result, patches = bytearray(original), []
    base = pe.OPTIONAL_HEADER.ImageBase
    for name, (va, height, call) in ROWS.items():
        offset = pe.get_offset_from_rva(va - base)
        if original[offset:offset+2] != bytes((0x6a, height)):
            raise ValueError(f'Unexpected row instruction: {name}')
        call_offset = pe.get_offset_from_rva(call - base)
        if original[call_offset:call_offset+5] != b'\xe8' + struct.pack('<i', 0x478b20-call-5):
            raise ValueError(f'Unexpected list constructor: {name}')
        result[offset+1] = ROW_HEIGHT
        patches.append(dict(name=name, address=hex(va+1), offset=offset+1, before=height, after=ROW_HEIGHT))
    if sum(a != b for a, b in zip(original, result, strict=True)) != len(ROWS):
        raise ValueError('Unexpected executable changes')
    return bytes(result), patches

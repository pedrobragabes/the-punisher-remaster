"""Offline binary/geometry checks. Does not start a game process or use its memory."""
import json
import struct
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EIP, UC_X86_REG_ESP, UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX, UC_X86_REG_EDX, UC_X86_REG_EBP, UC_X86_REG_ESI, UC_X86_REG_EDI
from punisher_lab import LAB, GAME, vpp_index, read_entry, digest
from menu_readability import ROWS, ROW_HEIGHT, LAYOUT, PATTERN, patch_rows
from inspect_ui import inspect_font


def emulator(executable):
    pe = pefile.PE(data=executable)
    mu = Uc(UC_ARCH_X86, UC_MODE_32)
    size = (pe.OPTIONAL_HEADER.SizeOfImage + 4095) & ~4095
    mu.mem_map(0x400000, size)
    mu.mem_write(0x400000, pe.get_memory_mapped_image())
    mu.mem_map(0x2000000, 0x10000)
    return mu


def read32(mu, address):
    return struct.unpack('<I', mu.mem_read(address, 4))[0]


def verify_constructors(executable):
    mu = emulator(executable)
    observed = {}
    def hook(mu, address, size, data):
        if address == 0x478b20:
            observed['object'] = mu.reg_read(UC_X86_REG_ECX)
            stack = mu.reg_read(UC_X86_REG_ESP)
            observed['name'] = bytes(mu.mem_read(read32(mu, stack+4), 60)).split(b'\0')[0].decode('ascii')
            observed['args_height'] = read32(mu, stack+48)
            observed['font'] = read32(mu, stack+40)
        if address == 0x477e80:
            # Stub only base-widget initialization; execute the actual derived constructor.
            stack = mu.reg_read(UC_X86_REG_ESP)
            ret = read32(mu, stack)
            mu.reg_write(UC_X86_REG_ESP, stack+44)
            mu.reg_write(UC_X86_REG_EIP, ret)
    mu.hook_add(UC_HOOK_CODE, hook)
    for name, (start, _, call) in ROWS.items():
        observed.clear()
        mu.reg_write(UC_X86_REG_ESP, 0x200e000)
        mu.reg_write(UC_X86_REG_ECX, 0)
        mu.reg_write(UC_X86_REG_EDX, 0)
        mu.emu_start(start-4, call+5, count=120)
        assert observed['name'] == name, (name, observed)
        assert observed['args_height'] == ROW_HEIGHT, (name, observed)
        assert observed['font'] == 0x676054, (name, observed)
        assert read32(mu, observed['object']+0x5c) == ROW_HEIGHT
        assert mu.reg_read(UC_X86_REG_ESP) == 0x200e000, name
    return len(ROWS)


def verify_hit_testing(executable):
    mu = emulator(executable)
    obj, stack = 0x2001000, 0x200e000
    count = 0
    for name in ROWS:
        x, y, width, height = LAYOUT[name]
        mu.mem_write(obj, bytes(0x100))
        for offset, value in [(0x2c,x), (0x30,y), (0x34,width), (0x38,height), (0x5c,ROW_HEIGHT)]:
            mu.mem_write(obj+offset, struct.pack('<I',value))
        for row in range(height//ROW_HEIGHT):
            for delta in (0, ROW_HEIGHT-1):
                mu.reg_write(UC_X86_REG_ESP, stack)
                mu.mem_write(stack, struct.pack('<4I',0,x+1,y+row*ROW_HEIGHT+delta,0))
                mu.reg_write(UC_X86_REG_ECX, obj)
                # Actual input path through origin subtraction, bounds check, and division.
                mu.emu_start(0x478fd0, 0x478ff9, count=30)
                assert mu.reg_read(UC_X86_REG_EAX) == row, (name,row,delta)
                count += 1
    return count


def verify_draw_rows(executable):
    mu = emulator(executable)
    obj, model, vtable, stack = 0x2001000, 0x2002000, 0x2003000, 0x200e000
    mu.mem_write(model, struct.pack('<I',vtable))
    mu.mem_write(vtable, struct.pack('<3I',0x2008000,0,0x2008100))
    observed = []
    rows = 8
    def hook(mu, address, size, data):
        if address not in (0x2008000,0x2008100):return
        sp = mu.reg_read(UC_X86_REG_ESP)
        ret = read32(mu,sp)
        if address == 0x2008100:
            # The original loop passes (widget, index, selected, rectangle by value).
            observed.append(tuple(read32(mu,sp+offset) for offset in (8,16,20,24,28)))
            mu.reg_write(UC_X86_REG_ESP,sp+32)
        else:
            mu.reg_write(UC_X86_REG_EAX,rows)
            mu.reg_write(UC_X86_REG_ESP,sp+4)
        mu.reg_write(UC_X86_REG_EIP,ret)
    mu.hook_add(UC_HOOK_CODE,hook)
    count = 0
    for name in ROWS:
        x,y,width,height = LAYOUT[name]
        rows = height//ROW_HEIGHT
        observed.clear()
        mu.mem_write(obj,bytes(0x100))
        for offset,value in [(0x3c,x),(0x5c,ROW_HEIGHT),(0x60,0),(0x64,model)]:
            mu.mem_write(obj+offset,struct.pack('<I',value))
        mu.mem_write(stack+0x10,struct.pack('<I',width))
        for reg,value in [(UC_X86_REG_ESI,obj),(UC_X86_REG_ESP,stack),(UC_X86_REG_EBX,y),(UC_X86_REG_EDI,0)]:
            mu.reg_write(reg,value)
        mu.emu_start(0x478d90,0x478dcd,count=rows*50)
        assert observed == [(i,x,y+i*ROW_HEIGHT,width,ROW_HEIGHT) for i in range(rows)], name
        assert mu.reg_read(UC_X86_REG_ESP) == stack
        count += rows
    return count


def verify_geometry():
    for name, (x,y,w,h) in LAYOUT.items():
        assert x >= 0 and y >= 0
        assert w == -1 or w > 0
        assert h == -1 or h > 0
        assert w == -1 or x+w <= 1920, name
        assert h == -1 or y+h <= 1080, name
        if name in ROWS:
            assert h % ROW_HEIGHT == 0, name
    assert LAYOUT['ap_action_list'][3] == 8*ROW_HEIGHT
    assert LAYOUT['wz_level_list'][3] == 16*ROW_HEIGHT
    # Test rendered bounds from the ORIGINAL video's actual dimensions, not table width.
    for screen_w,screen_h in [(1920,1080),(2560,1440)]:
        x,y,_,_ = LAYOUT['bf_movie']
        right, bottom = x+320*screen_w/640, y+240*screen_h/480
        assert right <= screen_w and bottom <= screen_h
        assert bottom+20 <= LAYOUT['bf_briefing_text'][1]
        assert LAYOUT['bf_action_list'][0]+LAYOUT['bf_action_list'][2]+30 <= x
        assert LAYOUT['bf_detail_bg'][0]+LAYOUT['bf_detail_bg'][2]+30 <= x
    return len(LAYOUT)


def verify_label_widths(root):
    archive = root/'dvd_pc/data/misc.vpp'
    entry = next(e for e in vpp_index(archive)['entries'] if e['name']=='interface.vf2')
    font = inspect_font(read_entry(archive,entry))
    assert font['height'] == 30 and ROW_HEIGHT >= font['height']+6
    samples = {
        'ap_action_list': ['WAR ZONE','ARMORY','UPGRADES','WAR JOURNAL','EXTRAS','OPTIONS','PROFILES','QUIT'],
        'wz_level_list': ['CRACKHOUSE','THE CHOP SHOP',"LUCKY'S BAR",'CENTRAL ZOO',"GREY'S FUNERAL HOME",'GNUCCI ESTATE','PIER 74','THE IGOR BALTIYSKY',"CASTLE'S APARTMENT",'GRAND NIXON ISLAND','FISK INDUSTRIES','PIER 74 REVISITED','MEAT PACKING PLANT','STARK TOWERS','THE TAKAGI BUILDING',"RYKER'S ISLAND"],
        'bf_action_list': ['START MISSION','CHANGE WEAPONS','DEFAULT WEAPONS','VIEW STATISTICS','CHALLENGE MODE'],
    }
    results=[]
    # Conservative unkerned extents; runtime font/layout behavior remains a separate check.
    for name, labels in samples.items():
        for label in labels:
            cursor=0;right=0
            for char in label:
                glyph=font['glyphs'][ord(char)-font['first_code']]
                right=max(right,cursor+glyph['width'])
                cursor+=glyph['advance']
            assert right+12 <= LAYOUT[name][2], (name,label,right)
            results.append(dict(widget=name,label=label,unkerned_width=right))
    return results


def main():
    root = LAB/'work/readability-candidate'
    report = json.loads((root/'manifest.json').read_text())
    for item in report['components']:
        assert digest((GAME/item['archive']).read_bytes()) == item['source_sha256']
        assert digest((root/item['archive']).read_bytes()) == item['output_sha256']
    exe = (root/'pun.exe').read_bytes()
    original = (GAME/'pun.exe').read_bytes()
    expected = {p['offset'] for p in report['components'][-1]['patches']}
    assert len(exe) == len(original)
    assert {i for i,(a,b) in enumerate(zip(original,exe)) if a != b} == expected
    mutated = bytearray(original); mutated[0] ^= 1
    try:
        patch_rows(mutated)
    except ValueError:
        pass
    else:
        raise AssertionError('Unsupported executable was accepted')
    # Verify the scope: every other preset, table, and archive entry is unchanged.
    for relative in ['dvd_pc/data/misc.vpp','dvd_pc/data/tables.vpp']:
        a = {e['name']:e for e in vpp_index(GAME/relative)['entries']}
        b = {e['name']:e for e in vpp_index(root/relative)['entries']}
        assert a.keys() == b.keys()
        allowed = {'interface.vf2','fonts.ceg'} if 'misc' in relative else {'gui.tbl'}
        for name in a.keys() - allowed:
            assert read_entry(GAME/relative,a[name]) == read_entry(root/relative,b[name])
        if 'tables' in relative:
            old = read_entry(GAME/relative,a['gui.tbl']).splitlines()
            new = read_entry(root/relative,b['gui.tbl']).splitlines()
            section = None
            for left,right in zip(old,new,strict=True):
                if left.startswith(b'#'): section = left.strip()[1:]
                if left != right:
                    assert section == b'1280x960'
                    assert PATTERN.match(left.decode('ascii'))[2] in LAYOUT
    result = dict(constructors=verify_constructors(exe), hit_test_cases=verify_hit_testing(exe),
                  draw_row_rectangles=verify_draw_rows(exe),
                  layout_rectangles=verify_geometry(), changed_executable_bytes=len(expected),
                  label_width_checks=len(verify_label_widths(root)),
                  game_started=False, installed=False, in_game_verified=False,
                  limits='Base-widget initialization is stubbed; runtime rendering, dynamic positioning, input devices, and video decoding are not tested.')
    (LAB/'reports/readability-verification.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))


if __name__ == '__main__':
    main()

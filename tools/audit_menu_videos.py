"""Audit local Bink candidates and emulate the known allocator crash site.

No game process is started and no installed files are changed. The memory-failure
experiment injects a null allocator result; it does not prove a runtime cause.
"""
import json
import struct
from collections import Counter
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_INVALID, UcError
from unicorn.x86_const import UC_X86_REG_EIP, UC_X86_REG_ESP, UC_X86_REG_EAX
from punisher_lab import LAB, GAME, digest
from build_menu_videos import header
from menu_readability import EXPECTED_EXE
from verify_readability import emulator, read32


def allocator_probe(original, allocation_result):
    mu = emulator(original)
    stack, stop = 0x200e000, 0x2009000
    mu.reg_write(UC_X86_REG_ESP, stack)
    mu.mem_write(stack, struct.pack('<2I',stop,4096))
    mu.mem_write(0xbc54b8, struct.pack('<I',7))
    faults = []
    def allocator(mu, address, size, data):
        if address != 0x526030:return
        sp = mu.reg_read(UC_X86_REG_ESP)
        assert read32(mu, sp+4) == 4096+256
        mu.reg_write(UC_X86_REG_EAX, allocation_result)
        mu.reg_write(UC_X86_REG_EIP, read32(mu,sp))
        mu.reg_write(UC_X86_REG_ESP, sp+4)
    def invalid(mu, access, address, size, value, data):
        faults.append(dict(instruction=hex(mu.reg_read(UC_X86_REG_EIP)),
                           address=hex(address), size=size, value=value))
        return False
    mu.hook_add(UC_HOOK_CODE, allocator)
    mu.hook_add(UC_HOOK_MEM_INVALID, invalid)
    try:
        mu.emu_start(0x557d30, stop, count=80)
    except UcError:
        if not faults:raise
    if allocation_result == 0:
        assert len(faults) == 1 and faults[0]['instruction'] == '0x557d64'
        assert faults[0]['address'] == '0xfc'
        return dict(injected_allocator_result=0, faults=faults)
    aligned = (allocation_result+256) & ~255
    assert not faults and mu.reg_read(UC_X86_REG_EAX) == aligned
    assert read32(mu,aligned-4) == aligned-allocation_result
    assert read32(mu,0xbc54b8) == 7
    assert mu.reg_read(UC_X86_REG_ESP) == stack+8
    return dict(injected_allocator_result=hex(allocation_result), returned=hex(aligned), preserved_state=True)


def main():
    original = (GAME/'pun.exe').read_bytes()
    if digest(original) != EXPECTED_EXE:
        raise ValueError('Unsupported executable for allocator analysis')
    manifest = json.loads((LAB/'reports/ui-video-manifest.json').read_text())
    if not manifest['complete']:
        raise ValueError('Incomplete video candidate set')
    results = []
    for item in sorted(manifest['videos'],key=lambda v:v['archive']):
        source = GAME/item['archive']
        output = LAB/'work/ui-pack'/item['archive']
        assert digest(source.read_bytes()) == item['source_sha256']
        assert digest(output.read_bytes()) == item['output_sha256']
        before, after = header(source), header(output)
        assert before == item['before'] and after == item['after']
        for key in ('frames','fps_num','fps_den','audio_tracks','magic'):
            assert before[key] == after[key], (item['archive'],key)
        test_file = LAB/'work/game'/item['archive']
        installed_hash = digest(test_file.read_bytes()) if test_file.exists() else None
        active = 'original' if installed_hash == item['source_sha256'] else (
            'converted' if installed_hash == item['output_sha256'] else 'unknown')
        results.append(dict(file=item['archive'], original_size=[before['width'],before['height']],
                            candidate_size=[after['width'],after['height']], active_test_copy=active,
                            pixel_area_multiplier=(after['width']*after['height'])/(before['width']*before['height']),
                            encoded_bytes_original=source.stat().st_size, encoded_bytes_candidate=output.stat().st_size,
                            rgba_frame_bytes_reference=after['width']*after['height']*4))
    report = dict(status='offline audit, no installation or launch',
                  videos=len(results), active_test_copy=dict(Counter(x['active_test_copy'] for x in results)),
                  area_multipliers=dict(Counter(str(x['pixel_area_multiplier']) for x in results)),
                  candidate_encoded_bytes=sum(x['encoded_bytes_candidate'] for x in results),
                  original_encoded_bytes=sum(x['encoded_bytes_original'] for x in results),
                  allocator_probes=[allocator_probe(original,0),allocator_probe(original,0x2004008),allocator_probe(original,0x2004100)],
                  conclusion='An injected null allocation reproduces the observed instruction offset. Runtime allocation failure, requested size, and its cause remain unconfirmed.',
                  limits='RGBA frame bytes are an illustrative reference, not measured Bink memory usage. No full-frame decoding or runtime test is performed here.',
                  files=results, in_game_verified=False)
    (LAB/'reports/menu-video-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='files'}))


if __name__ == '__main__':
    main()

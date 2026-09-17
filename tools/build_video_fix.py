"""Version-locked rendering patch, only emitted to the isolated UI package.

The game overwrites movie widget dimensions from Bink width/height and then
multiplies them by desktop/640x480. New videos therefore require compensation
both when opening the widget and when drawing. Never patch shared constants.
"""
import json
import struct
import pefile
from keystone import Ks,KS_ARCH_X86,KS_MODE_32
from punisher_lab import LAB,GAME,digest

EXPECTED='de995c66c7388532942264aa2d9455ac5d10e254d0713aeacd3ea0690098878a'


def align(n,a):return (n+a-1)//a*a


def main():
    original=(GAME/'pun.exe').read_bytes()
    if digest(original)!=EXPECTED:raise ValueError('Unsupported executable; refusing binary patch')
    pe=pefile.PE(data=original)
    assert pe.OPTIONAL_HEADER.ImageBase==0x400000 and not pe.OPTIONAL_HEADER.DllCharacteristics & 0x40
    header_offset=pe.sections[-1].get_file_offset()+40
    assert header_offset+40<=pe.sections[0].PointerToRawData
    # Version-locked file has an unreferenced marker in section-header slack.
    # No data directory points into this range; retain the bytes in the manifest.
    original_header_slack=original[header_offset:header_offset+40].hex()
    rva=align(pe.sections[-1].VirtualAddress+pe.sections[-1].Misc_VirtualSize,pe.OPTIONAL_HEADER.SectionAlignment)
    raw_offset=align(len(original),pe.OPTIONAL_HEADER.FileAlignment)
    asm=Ks(KS_ARCH_X86,KS_MODE_32)
    code=bytearray();functions={}
    for dimension,divisor in [('width',4),('height',3)]:
        address=0x400000+rva+len(code);functions[dimension]=address
        text=f'''
            call 0x5da43c
            pushfd
            push ecx
            push edx
            mov ecx, dword ptr [0x10ffecc]
            test ecx,ecx
            jz done
            cmp dword ptr [ecx],1280
            je half
            cmp dword ptr [ecx],960
            jne done
            mov ecx,{divisor}
            jmp divide
        half:
            mov ecx,2
        divide:
            xor edx,edx
            div ecx
        done:
            pop edx
            pop ecx
            popfd
            ret
        '''
        compiled,_=asm.asm(text,addr=address)
        code.extend(compiled)
    output=bytearray(original)
    patches=[]
    for va,dimension in [(0x47795c,'width'),(0x477978,'height'),(0x557fce,'width'),(0x557fa0,'height')]:
        offset=pe.get_offset_from_rva(va-0x400000)
        before=b'\xe8'+struct.pack('<i',0x5da43c-va-5)
        assert original[offset:offset+5]==before
        after=b'\xe8'+struct.pack('<i',functions[dimension]-va-5)
        output[offset:offset+5]=after
        patches.append(dict(address=hex(va),before=before.hex(),after=after.hex(),dimension=dimension))
    raw_size=align(len(code),pe.OPTIONAL_HEADER.FileAlignment)
    section=struct.pack('<8sIIIIIIHHI',b'.uifix\0\0',len(code),rva,raw_size,raw_offset,0,0,0,0,0x60000020)
    output[header_offset:header_offset+40]=section
    struct.pack_into('<H',output,pe.FILE_HEADER.get_field_absolute_offset('NumberOfSections'),len(pe.sections)+1)
    struct.pack_into('<I',output,pe.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(rva+len(code),pe.OPTIONAL_HEADER.SectionAlignment))
    struct.pack_into('<I',output,pe.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfCode'),pe.OPTIONAL_HEADER.SizeOfCode+raw_size)
    output.extend(bytes(raw_offset-len(output)));output.extend(code);output.extend(bytes(raw_size-len(code)))
    parsed=pefile.PE(data=bytes(output))
    struct.pack_into('<I',output,pe.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),parsed.generate_checksum())
    target=LAB/'work/ui-pack/pun.exe';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(output)
    report=dict(archive='pun.exe',source_sha256=EXPECTED,output_sha256=digest(output),patches=patches,functions=functions,original_header_slack=original_header_slack,
                in_game_verified=False,scope='Compensates movie dimensions for 1280x960 menu and 960x720 briefing assets. Other video widths retain original calculation.')
    (LAB/'reports/ui-exe-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

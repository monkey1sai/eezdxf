#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import subprocess
import shlex
import shutil
import sys

PYTHON3 = "python"
POSIX = sys.platform != "win32"
if POSIX:
    PYTHON3 = shutil.which("python3")


def main():
    filepath = Path(__file__)
    for script in filepath.parent.glob("create_*.py"):
        cmd = f"{PYTHON3} {script}"
        print(f'executing: "{cmd}"')
        args = shlex.split(cmd, posix=POSIX)
        subprocess.run(args)


if __name__ == "__main__":
    from ezdxf.addons.importer import Importer
    import ezdxf
    dimdoc = ezdxf.readfile(r'D:\._vscode2\ezdxf-sorc\examples_dxf\wipeout_door.dxf')
    newdoc = ezdxf.new(dxfversion=dimdoc.dxfversion, setup=True)
    imper =  Importer(dimdoc, newdoc)

    dimdoc2 = ezdxf.readfile(r'D:\._vscode2\ezdxf-sorc\examples_dxf\dimension_in_nested_blocks.dxf')
    newdoc2 = ezdxf.new(dxfversion=dimdoc.dxfversion, setup=True)
    imper2 =  Importer(dimdoc2, newdoc2)


    print('')
    main()

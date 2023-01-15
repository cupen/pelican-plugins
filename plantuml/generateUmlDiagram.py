#!/usr/bin/env python
import logging
import os
import tempfile
from zlib import adler32
from subprocess import Popen, PIPE
from pelican import logger
import hashlib


def name_with_hash(b):
    h = hashlib.md5()
    h.update(b.encode("utf-8"))
    return h.hexdigest()


def plantuml_render_to_file(code, fmt, fpath):
    fname = os.path.basename(fpath)
    work_dir = tempfile.mkdtemp(prefix="plantuml_render")
    src = os.path.join(work_dir, fname).split(".")[0] + ".puml"
    with open(src, "w") as fp:
        fp.write('@startuml\n')
        fp.write(code)
        fp.write('\n@enduml\n')
    
    to_dir  = os.path.dirname(fpath)

    logger.debug("[plantuml] Temporary PlantUML source at "+(src))
    if fmt == 'png':
        file_ext = ".png"
        outopt = "-tpng"
    elif fmt == 'svg':
        file_ext = ".svg"
        outopt = "-tsvg"
    else:
        logger.error("Bad uml image format '"+ fmt +"', using png")
        file_ext = ".png"
        outopt = "-tpng"

    cmdline = ['plantuml', '-o', to_dir, outopt, src]

    try:
        logger.debug("[plantuml] About to execute "+" ".join(cmdline))
        p = Popen(cmdline, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
    except Exception as exc:
        raise Exception('Failed to run plantuml: %s' % exc)
    else:
        if p.returncode != 0:
            raise RuntimeError('Error calling plantuml: %s' % err)
        # diagram was correctly generated, we can remove the temporary file (if not debugging)
        if not logger.isEnabledFor(logging.DEBUG):
            os.remove(src)
        pass
    pass


def plantuml_render(code, fmt):
    fpath = plantuml_render_to_file(code, fmt)
    with open(fpath) as fp:
        return fp.read()
    pass
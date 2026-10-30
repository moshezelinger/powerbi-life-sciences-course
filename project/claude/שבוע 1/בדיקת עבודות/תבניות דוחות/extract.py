import sys, os, zipfile, re, hashlib
from docx import Document
from docx.oxml.ns import qn
root, outdir = sys.argv[1], sys.argv[2]
for dp, dn, fn in os.walk(root):
    for f in sorted(fn):
        if not f.endswith('.docx'): continue
        p = os.path.join(dp, f)
        student = os.path.basename(dp).split('_')[0]
        group = os.path.relpath(p, root).split(os.sep)[0]
        od = os.path.join(outdir, group, student); os.makedirs(od, exist_ok=True)
        d = Document(p)
        rels = d.part.rels
        lines = []
        imgn = [0]
        def walk(el):
            for child in el.iterchildren():
                tag = child.tag
                if tag == qn('w:p'):
                    txt = []
                    for node in child.iter():
                        if node.tag == qn('w:t') and node.text: txt.append(node.text)
                        elif node.tag == qn('w:tab'): txt.append('\t')
                        elif node.tag in (qn('w:br'),): txt.append('\n')
                        elif node.tag == qn('a:blip'):
                            rid = node.get(qn('r:embed'))
                            if rid and rid in rels:
                                part = rels[rid].target_part
                                imgn[0]+=1
                                ext = os.path.splitext(part.partname)[1]
                                name = f"{os.path.splitext(f)[0][:20]}_img{imgn[0]}{ext}"
                                open(os.path.join(od, name),'wb').write(part.blob)
                                txt.append(f"[[IMAGE {name} md5={hashlib.md5(part.blob).hexdigest()[:8]} {len(part.blob)}B]]")
                    lines.append(''.join(txt))
                elif tag == qn('w:tbl'):
                    for row in child.iter(qn('w:tr')):
                        cells=[]
                        for c in row.iter(qn('w:tc')):
                            cells.append(' '.join(t.text or '' for t in c.iter(qn('w:t'))))
                        lines.append(' | '.join(cells))
                elif tag == qn('w:sdt'):
                    walk(child.find(qn('w:sdtContent')) if child.find(qn('w:sdtContent')) is not None else child)
        walk(d.element.body)
        with open(os.path.join(od, os.path.splitext(f)[0][:40]+'.txt'),'w') as fh:
            fh.write(f"FILE: {f}\n" + '\n'.join(lines))

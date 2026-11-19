"""Compare visible red marker footprints after registering the two original PDF figures."""
import argparse
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np


def words(page, labels):
    result = []
    for a in page.get_text("words"):
        if a[4] in labels and (page.rect.width < 550 or a[3] < 282):
            result.append((a[4], (a[0]+a[2])/2, (a[1]+a[3])/2))
    return result


def render(page, zoom):
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom,zoom),colorspace=fitz.csRGB)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h,pix.w,3)


def red(rgb):
    return rgb[...,0].astype(int) - rgb[...,1].astype(int) >= 32


def read(path, expected):
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected
    return fitz.open(stream=data, filetype="pdf")


def compare(author, journal):
    original = read(author,'ade8ac17497ac11a3b8cf6392099a732475fde846cca5659ccb226f152fddd79')
    published = read(journal,'3b04c31c7e1ca68be38a3e1c519f8057d0e4af32fc76b086223f2c01056e1a14')
    source, target = original[0], published[8]
    ticks = {'A/A','A/G','G/G'}
    a = sorted(words(source,ticks),key=lambda w:w[1])
    b = sorted(words(target,ticks),key=lambda w:w[1])
    assert len(a)==len(b)==9 and [w[0] for w in a]==[w[0] for w in b]
    ax,bx = np.polyfit([w[1] for w in a],[w[1] for w in b],1)
    a = sorted(words(source, {'10','20','30'}))
    b = sorted(words(target, {'10','20','30'}))
    assert len(a)==len(b)==3 and [w[0] for w in a]==[w[0] for w in b]
    ay,by = np.polyfit([w[2] for w in a],[w[2] for w in b],1)
    z = 4
    src,tgt=red(render(source,z)),red(render(target,z))
    # Coordinates bracket plotting panels only. Text centers give approximate
    # registration, as fonts can differ between the two PDF versions.
    Ys = np.arange(23*z,249*z)
    Xs = np.arange(36*z,499*z)
    ref = src[np.ix_(Ys,Xs)]
    g = np.arange(-1.5,1.501,.25)
    best = (0,0,0,0,0,0)
    for dx in g:
        tx = np.rint((Xs+0.5)*ax+(bx+dx)*z-.5).astype(int)
        for dy in g:
            ty = np.rint((Ys+.5)*ay+(by+dy)*z-.5).astype(int)
            other = tgt[np.ix_(ty,tx)]
            intersection = np.count_nonzero(ref & other)
            union = np.count_nonzero(ref | other)
            item=(intersection/union,dx,dy,intersection,ref.sum(),other.sum())
            if item[0]>best[0]: best=item
    return dict(author_page=1,published_page=9,registered_region_source_points=[36,23,499,249],
                red_mask="red minus green at least 32 on 8-bit RGB",
                samples_per_source_point_per_axis=z,
                author_red_pixels=int(best[4]),published_red_pixels=int(best[5]),
                overlap_pixels=int(best[3]),intersection_over_union=round(float(best[0]),5),
                label_based_residual_shift_points=[float(best[1]),float(best[2])],
                scale_xy=[round(ax,7),round(ay,7)],
                translation_xy_points=[round(bx+best[1],5),round(by+best[2],5)])


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('author',type=Path)
    p.add_argument('journal',type=Path)
    a=p.parse_args()
    print(json.dumps(compare(a.author,a.journal),indent=2))

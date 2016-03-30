import argparse
import schlib
import copy
from math import cos, sin, ceil


def rect_bounds(r):
    startx = int(r['startx'])
    starty = int(r['starty'])
    endx   = int(r['endx'  ])
    endy   = int(r['endy'  ])
    return [min(startx, endx), min(starty, endy), max(startx, endx), max(starty, endy)]

def poly_bounds(p):
    flat_points = p["points"]
    points = [[int(flat_points[i]),int(flat_points[i+1])] for i in range(0, len(flat_points), 2)]
    coords = zip(*points)
    return [min(coords[0]), min(coords[1]), max(coords[0]), max(coords[1])]

def circle_bounds(c):
    posx    = int(c['posx'  ])
    posy    = int(c['posy'  ])
    radius  = int(c['radius'])
    return [posx - radius, posy - radius, posx + radius, posy + radius]

def arc_bounds(a):
    posx        = int(a['posx'])
    posy        = int(a['posy'])
    radius      = int(a['radius'])
    start_angle = float(a['start_angle'])/10.0
    end_angle   = float(a['end_angle'])/10.0
    start_point = [posx + int(radius*cos(start_angle)), posy + int(radius*sin(start_angle))]
    end_point   = [posx + int(radius*cos(end_angle)), posy + int(radius*sin(end_angle))]
    closest_right_end = ceil(end_angle/90.0)*90.0
    points = [start_point, end_point]
    while closest_right_end < end_angle:
        points.append([[posx + int(radius*cos(closest_right_end)), posy + int(radius*sin(closest_right_end))]])
        closest_right_end = closest_right_end + 90.0
    coords = zip(*points)
    return [min(coords[0]), min(coords[1]), max(coords[0]), max(coords[1])]

def pin_bounds(p):
    posx      = int(p['posx'     ])
    posy      = int(p['posy'     ])
    length    = int(p['length'   ])
    direction = p['direction']
    if direction == 'D':
        return [posx, posy - length, posx, posy]
    elif direction == 'U':
        return [posx, posy, posx, posy + length]
    elif direction == 'L':
        return [posx - length, posy, posx, posy]
    else:
        return [posx, posy, posx + length, posy]

def cross_nopop(component, rect):
    name = component.name
    component.name = name + "_NOPOP"
    component.definition["name"]= component.name
    component.fields[1]["name"] = '"' + component.name + '"'
    component.aliasesOrdered = [ a+ "_NOPOP" for a in component.aliasesOrdered]
    values = [ '2', '0', '1', '50', [str(rect[0]), str(rect[1]), str(rect[2]), str(rect[3])], "N"]
    component.draw['polylines'].append(dict(zip(component._POLY_KEYS,values)))
    component.drawOrdered.append(['P',component.draw['polylines'][-1]])
    values = [ '2', '0', '1', '50', [str(rect[0]), str(rect[3]), str(rect[2]), str(rect[1])], "N"]
    component.draw['polylines'].append(dict(zip(component._POLY_KEYS,values)))
    component.drawOrdered.append(['P', component.draw['polylines'][-1]])

def compute_boundaries(npcomp):
    boundaries = [[0, 0, 0, 0]]
    boundaries.extend([rect_bounds(r) for r in npcomp.draw["rectangles"]])
    boundaries.extend([poly_bounds(p) for p in npcomp.draw["polylines"]])
    boundaries.extend([circle_bounds(c) for c in npcomp.draw["circles"]])
    boundaries.extend([arc_bounds(a) for a in npcomp.draw["arcs"]])
    boundaries.extend([pin_bounds(p) for p in npcomp.draw["pins"]])
    coords = zip(*boundaries)
    rect = (min(coords[0]), min(coords[1]), max(coords[2]), max(coords[3]))
    return rect
    
def action(mylib, nopop=cross_nopop):
    components_names = set([c.name for c in mylib.components if c.definition["reference"] != "#PWR"])
    pop_set, nopop_set = set(), set()
    for c in components_names:
        nopop_set.add(c[:-6]) if c.endswith("_NOPOP") else pop_set.add(c)
    for c_name in pop_set - nopop_set:
        npcomp = copy.deepcopy(mylib.getComponentByName(c_name))
        rect = compute_boundaries(npcomp)
        nopop(npcomp, rect)
        mylib.components.append(npcomp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("libname")

    args = parser.parse_args()

    mylib = schlib.SchLib(args.libname)
    action(mylib)
    mylib.save()

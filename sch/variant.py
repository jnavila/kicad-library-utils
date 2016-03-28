# -*- coding: utf-8 -*-
import argparse
import sch

def variant(mysch, key_field, nopop_flag="NP"):
    kf = '"' + key_field + '"'
    npop = '"' + nopop_flag + '"'
    for comp in mysch.components:
        fields = [ f['ref'] for f in comp.fields if f['name'] == kf]
        if len(fields)>0 and fields[0] == npop:
            comp.labels["name"] = comp.labels["name"] + "_NOPOP"
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="change parts in schematic to reflect not variant BOM. You should have run create_nopop on the cache lib of the project before.")
    parser.add_argument("schematic")
    parser.add_argument('--key', dest='key', required=True,
                   help='key field for defining no pop')
    parser.add_argument('--nopop', dest="nopop_flag", default="NP",
                        help="value indicating that part is not populated")
    args = parser.parse_args()

    mysch = sch.Schematic(args.schematic)
    variant(mysch, key_field=args.key, nopop_flag=args.nopop_flag)
    mysch.save()

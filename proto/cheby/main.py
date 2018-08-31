#!/usr/bin/env python
import sys
import os.path
import time
import argparse
import cheby.parser
import cheby.pprint as pprint
import cheby.sprint as sprint
import cheby.cprint as cprint
import cheby.gen_laychk as gen_laychk
import cheby.layout as layout
import cheby.gen_hdl as gen_hdl
import cheby.print_vhdl as print_vhdl
import cheby.print_verilog as print_verilog
import cheby.print_encore as print_encore
import cheby.expand_hdl as expand_hdl
import cheby.gen_name as gen_name
import cheby.gen_gena_memmap as gen_gena_memmap
import cheby.gen_gena_regctrl as gen_gena_regctrl
import cheby.gen_wbgen_hdl as gen_wbgen_hdl
import cheby.print_html as print_html


def decode_args():
    aparser = argparse.ArgumentParser(description='cheby utility')
    aparser.add_argument('--print-pretty', action='store_true',
                         help='display the input in YAML')
    aparser.add_argument('--print-simple', action='store_true',
                         help='display the layout with fields')
    aparser.add_argument('--print-simple-expanded', action='store_true',
                         help='display the expanded layout with fields')
    aparser.add_argument('--print-pretty-expanded', action='store_true',
                         help='display the expanded input in YAML')
    aparser.add_argument('--print-memmap', action='store_true',
                         help='display the layout without fields')
    aparser.add_argument('--print-c', action='store', nargs='?', const='.',
                         help='display the c header file')
    aparser.add_argument('--print-c-check-layout', action='store_true',
                         help='generate c file to check layout of the header')
    aparser.add_argument('--hdl', choices=['vhdl', 'verilog'], default='vhdl',
                         help='select language for hdl generation')
    aparser.add_argument('--gen-hdl', action='store_true',
                         help='generate hdl file')
    aparser.add_argument('--gen-encore', action='store_true',
                         help='generate encore file')
    aparser.add_argument('--gen-gena-memmap', action='store_true',
                         help='generate Gena MemMap file')
    aparser.add_argument('--gen-gena-regctrl', action='store_true',
                         help='generate Gena RegCtrl file')
    aparser.add_argument('--gen-wbgen-hdl', action='store_true',
                         help='generate wbgen hdl')
    aparser.add_argument('--gen-doc', action='store_true',
                         help='generate documentation (html)')
    aparser.add_argument('FILE', nargs='+')

    return aparser.parse_args()


def print_hdl(out, lang, h):
    if lang == 'vhdl':
        print_vhdl.print_vhdl(out, h)
    elif lang == 'verilog':
        print_verilog.print_verilog(out, h)
    else:
        raise AssertionError('unknown hdl language {}'.format(lang))


def handle_file(args, filename):
    t = cheby.parser.parse_yaml(filename)

    layout.layout_cheby(t)

    if args.print_pretty:
        pprint.pprint_cheby(sys.stdout, t)
    if args.print_memmap:
        sprint.sprint_cheby(sys.stdout, t, False)
    if args.print_simple:
        sprint.sprint_cheby(sys.stdout, t, True)
    if args.print_c is not None:
        if args.print_c == '-':
            cprint.cprint_cheby(sys.stdout, t)
        else:
            if args.print_c == '.':
                name = t.name + '.h'
            else:
                name = args.print_c
            fd = open(name, 'w')
            cprint.cprint_cheby(fd, t)
            fd.close()
    if args.print_c_check_layout:
        gen_laychk.gen_chklayout_cheby(sys.stdout, t)
    if args.gen_encore:
        print_encore.print_encore(sys.stdout, t)
    if args.gen_gena_memmap:
        h = gen_gena_memmap.gen_gena_memmap(t)
        print_vhdl.print_vhdl(sys.stdout, h)
    # Decode x-hdl
    expand_hdl.expand_hdl(t)
    if args.print_simple_expanded:
        sprint.sprint_cheby(sys.stdout, t, True)
    if args.print_pretty_expanded:
        pprint.pprint_cheby(sys.stdout, t)
    if args.gen_gena_regctrl:
        if not args.gen_gena_memmap:
            gen_gena_memmap.gen_gena_memmap(t)
        h = gen_gena_regctrl.gen_gena_regctrl(t)
        print_vhdl.print_vhdl(sys.stdout, h)
    if args.gen_doc:
        print_html.pprint(t, sys.stdout)
    if args.gen_wbgen_hdl:
        h = gen_wbgen_hdl.expand_hdl(t)
        (basename, _) = os.path.splitext(os.path.basename(filename))
        c = {'vhdl': '--', 'verilog': '//'}[args.hdl]
        l = c[0] * 79
        ext = {'vhdl': 'vhdl', 'verilog': 'v'}[args.hdl]
        sys.stdout.write(
"""{l}
{c} Title          : Wishbone slave core for {name}
{l}
{c} File           : {basename}.{ext}
{c} Author         : auto-generated by wbgen2 from {basename}.wb
{c} Created        : {date}
{c} Standard       : VHDL'87
{l}
{c} THIS FILE WAS GENERATED BY wbgen2 FROM SOURCE FILE {basename}.wb
{c} DO NOT HAND-EDIT UNLESS IT'S ABSOLUTELY NECESSARY!
{l}

""".format(name=t.description, basename=basename,
           date=time.strftime("%a %b %d %X %Y"), c=c, l=l, ext=ext))
        print_vhdl.style = 'wbgen'
        print_hdl(sys.stdout, args.hdl, h)
    if args.gen_hdl:
        gen_name.gen_name_root(t)
        h = gen_hdl.generate_hdl(t)
        print_hdl(sys.stdout, args.hdl, h)


def main():
    args = decode_args()
    for f in args.FILE:
        try:
            handle_file(args, f)
        except cheby.parser.ParseException as e:
            sys.stderr.write("{}:parse error: {}\n".format(f, e.msg))
            sys.exit(2)
        except layout.LayoutException as e:
            sys.stderr.write("{}:layout error: {}\n".format(
                e.node.get_root().c_filename, e.msg))
            sys.exit(2)
        except gen_hdl.HdlError as e:
            sys.stderr.write("{}:HDL error: {}\n".format(f, e.msg))
            sys.exit(2)


if __name__ == '__main__':
    main()

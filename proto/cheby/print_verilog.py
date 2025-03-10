"""Generate Verilog from HDL tree"""

import cheby.hdltree as hdltree
from cheby.wrutils import w, wln, windent

style = None


def generate_header(_fd, _module):
    pass


def generate_verilog_kind(p):
    return "reg" if p.p_vlg_reg else "wire"


def generate_verilog_type(p):
    if p.size is not None:
        if isinstance(p.size, int):
            hi = str(p.lo_idx + p.size - 1)
        else:
            assert p.lo_idx == 0
            hi = generate_expr(p.size)
        return "[{}:{}] ".format(hi, p.lo_idx)
    else:
        return ""


def generate_decl_comment(fd, comment, indent):
    if comment is None:
        return
    # Reindent comment.
    for l in comment.split('\n'):
        if l == '':
            wln(fd)
        else:
            windent(fd, indent)
            wln(fd, "// {}".format(l))


def generate_port(fd, p, indent):
    generate_decl_comment(fd, p.comment, indent)
    typ = generate_verilog_type(p)
    if p.dir == 'IN':
        iodir = "input  "
    elif p.dir == 'OUT':
        iodir = "output "
    else:
        iodir = "inout  "
    windent(fd, indent)
    w(fd, "{iodir} {kind} {typ}{name}".format(
        iodir=iodir, kind=generate_verilog_kind(p), typ=typ, name=p.name))
    if p.default:
        w(fd, ' = {}'.format(generate_expr(p.default)))


def generate_interface_port(fd, itf, dirn, indent):
    for p in itf.ports:
        if p.dir == dirn:
            windent(fd, indent + 1)
            wln(fd, "{:<16} : {};".format(p.name, generate_verilog_type(p)))


def generate_interface(fd, itf, indent):
    generate_decl_comment(fd, itf.comment, indent)
    windent(fd, indent)
    wln(fd, "type {}_master_out is record".format(itf.name))
    generate_interface_port(fd, itf, 'OUT', indent)
    windent(fd, indent)
    wln(fd, "end record {}_master_out;".format(itf.name))
    windent(fd, indent)
    wln(fd, "subtype {0}_slave_in is {0}_master_out;".format(itf.name))
    wln(fd)
    windent(fd, indent)
    wln(fd, "type {}_slave_out is record".format(itf.name))
    generate_interface_port(fd, itf, 'IN', indent)
    windent(fd, indent)
    wln(fd, "end record {}_slave_out;".format(itf.name))
    windent(fd, indent)
    wln(fd, "subtype {0}_master_in is {0}_slave_out;".format(itf.name))


def generate_param(fd, p, indent):
    generate_decl_comment(fd, p.comment, indent)
    typ = generate_verilog_type(p)
    windent(fd, indent)
    w(fd, "{} : {typ}".format(p.name, typ=typ))
    if p.value:
        w(fd, " := {}".format(generate_expr(p.value)))


def generate_signal(fd, s, indent):
    typ = generate_verilog_type(s)
    windent(fd, indent)
    w(fd, "{} {}{};\n".format(generate_verilog_kind(s), typ, s.name))


def generate_constant(fd, s, indent):
    typ = generate_verilog_type(s)
    windent(fd, indent)
    w(fd, "localparam {}{} = {};".format(
        typ, s.name, generate_expr(s.value)))
    if hasattr(s, 'eol_comment'):
        w(fd, "// " + s.eol_comment)
    wln(fd)


def generate_decl(fd, d, indent):
    if isinstance(d, hdltree.HDLSignal):
        generate_signal(fd, d, indent)
    elif isinstance(d, hdltree.HDLConstant):
        generate_constant(fd, d, indent)
    elif isinstance(d, hdltree.HDLComponent):
        pass
    elif isinstance(d, hdltree.HDLComponentSpec):
        pass
    elif isinstance(d, hdltree.HDLComment):
        generate_comment(fd, d, indent)
    elif isinstance(d, hdltree.HDLInterface):
        generate_interface(fd, d, indent)
    else:
        raise AssertionError(d)


operator = {hdltree.HDLAnd: (' & ', 4),
            hdltree.HDLOr:  (' | ', 3),
            hdltree.HDLNot: ('!', 5),
            hdltree.HDLSub: ('-', 1),
            hdltree.HDLMul: ('*', 2),
            hdltree.HDLEq:  (' == ', 5),
            hdltree.HDLGe:  (' >= ', 5),
            hdltree.HDLLe:  (' <= ', 5)}


def generate_concat_inner(e):
    assert isinstance(e, hdltree.HDLConcat)
    # Try to linearize nested concatenations (at least on the lhs)
    if isinstance(e.left, hdltree.HDLConcat):
        res = generate_concat_inner(e.left)
    else:
        res = generate_expr(e.left)
    res += ', ' + generate_expr(e.right)
    return res


def generate_expr(e, prio=-1):
    if isinstance(e, hdltree.HDLObject):
        return e.name
    elif isinstance(e, hdltree.HDLConcat):
        return '{' + generate_concat_inner(e) + '}'
    elif isinstance(e, hdltree.HDLBinary):
        opname, opprio = operator[type(e)]
        res = ''.join([generate_expr(e.left, opprio),
                       opname,
                       generate_expr(e.right, opprio)])
        if opprio <= prio:
            return "({})".format(res)
        else:
            return res
    elif isinstance(e, hdltree.HDLUnary):
        opname, opprio = operator[type(e)]
        res = "{}{}".format(opname, generate_expr(e.expr, opprio))
        if opprio <= prio:
            return "({})".format(res)
        else:
            return res
    elif isinstance(e, hdltree.HDLParen):
        return "({})".format(generate_expr(e.expr))
    elif isinstance(e, hdltree.HDLReplicate):
        if e.expr == hdltree.bit_0:
            return "{}'b0".format(e.num)
        return "{{{}{{{}}}}}".format(e.num, generate_expr(e.expr))
    elif isinstance(e, hdltree.HDLZext):
        return generate_expr(e.expr)
    elif isinstance(e, hdltree.HDLSext):
        return generate_expr(e.expr)
    elif isinstance(e, hdltree.HDLBit):
        return "1'b{}".format(e.val)
    elif isinstance(e, hdltree.HDLUndef):
        return "1'bx"
    elif isinstance(e, hdltree.HDLHexConst):
        assert (e.size > 0 and (e.size % 4) == 0)
        res = "{}'h".format(e.size)
        for i in range(e.size - 4, -1, -4):
            res += '{:X}'.format((e.val >> i) & 15)
        return res
    elif isinstance(e, hdltree.HDLConst) or isinstance(e, hdltree.HDLBinConst):
        if e.size is None:
            # A bit.
            return "1'b{}".format(e.val)

        # Certainly overkill, patches welcome!
        res = "{}'b".format(e.size)
        for i in range(e.size - 1, -1, -1):
            res += '1' if ((e.val >> i) & 1) == 1 else '0'
        return res
    elif isinstance(e, hdltree.HDLNumber):
        return "{}".format(e.val)
    elif isinstance(e, hdltree.HDLBool):
        if e.val:
            return "1'b1"
        else:
            return "1'b0"
    elif isinstance(e, hdltree.HDLSlice):
        if e.size is None:
            return "{}[{}]".format(generate_expr(e.prefix), e.index)
        else:
            return "{}[{}:{}]".format(
                generate_expr(e.prefix), e.index + e.size - 1, e.index)
    elif isinstance(e, hdltree.HDLIndex):
        return "{}[{}]".format(generate_expr(e.prefix), e.index)
    elif isinstance(e, hdltree.HDLInterfaceSelect):
        return "{}.{}".format(e.prefix.name, e.subport.name)
    else:
        assert False, "unhandled hdl expr {}".format(e)


def get_base_name(s):
    if isinstance(s, hdltree.HDLObject):
        return s
    elif isinstance(s, hdltree.HDLSlice) or isinstance(s, hdltree.HDLIndex):
        return get_base_name(s.prefix)
    elif isinstance(s, hdltree.HDLInterfaceSelect):
        return get_base_name(s.subport)
    else:
        return None


def generate_assign(fd, s):
    targ = generate_expr(s.target)
    expr = generate_expr(s.expr)
    wln(fd, "assign {} = {};".format(targ, expr))


def generate_seq_block(fd, stmts, level):
    # Count number of statements.  FIXME: use functional syntax ?
    nbr_stmts = 0
    for s in stmts:
        if not isinstance(s, hdltree.HDLComment):
            nbr_stmts += 1

    if nbr_stmts <= 1:
        # At most one statement: do not use blocks, but there can be several
        # comments.
        for s in stmts:
            generate_seq(fd, s, level)
        if nbr_stmts == 0:
            # null (there is no statement)
            w(fd, '  ' * level)
            wln(fd, ';')
    else:
        # More than one statement: use a block
        indent = '  ' * level
        wln(fd, indent + "begin")
        for s in stmts:
            generate_seq(fd, s, level + 1)
        wln(fd, indent + "end")


def generate_seq(fd, s, level):
    indent = '  ' * level
    if isinstance(s, hdltree.HDLAssign):
        w(fd, indent)
        targ = generate_expr(s.target)
        expr = generate_expr(s.expr)
        wln(fd, "{} <= {};".format(targ, expr))
    elif isinstance(s, hdltree.HDLIfElse):
        w(fd, indent)
        while True:
            wln(fd, "if ({})".format(generate_expr(s.cond)))
            generate_seq_block(fd, s.then_stmts, level + 1)
            if s.else_stmts is None:
                break
            w(fd, indent)
            if len(s.else_stmts) == 1 \
               and isinstance(s.else_stmts[0], hdltree.HDLIfElse):
                w(fd, "else ")
                s = s.else_stmts[0]
            else:
                wln(fd, "else")
                generate_seq_block(fd, s.else_stmts, level + 1)
                break
    elif isinstance(s, hdltree.HDLSwitch):
        w(fd, indent)
        wln(fd, "case ({})".format(generate_expr(s.expr)))
        for c in s.choices:
            w(fd, indent)
            if isinstance(c, hdltree.HDLChoiceExpr):
                wln(fd, "{}: ".format(generate_expr(c.expr)))
            elif isinstance(c, hdltree.HDLChoiceDefault):
                wln(fd, "default:")
            generate_seq_block(fd, c.stmts, level + 1)
        wln(fd, indent + "endcase")
    elif isinstance(s, hdltree.HDLComment):
        w(fd, indent)
        wln(fd, "// {}".format(s.comment))
    else:
        assert False, "unhandled hdl seq {}".format(s)


def generate_comment(fd, n, indent):
    if n.nl:
        wln(fd)
    if n.comment is not None:
        windent(fd, indent)
        wln(fd, "// {}".format(n.comment))


def generate_stmts(fd, stmts, indent):
    sindent = "  " * indent
    gen_num = 0
    for s in stmts:
        if isinstance(s, hdltree.HDLComment):
            generate_comment(fd, s, indent)
        elif isinstance(s, hdltree.HDLAssign):
            w(fd, sindent)
            generate_assign(fd, s)
        elif isinstance(s, hdltree.HDLComb):
            w(fd, sindent)
            if s.name is not None:
                w(fd, '{}: '.format(s.name))
            w(fd, "always @(")
            first = True
            for e in s.sensitivity:
                if first:
                    first = False
                else:
                    w(fd, ", ")
                w(fd, generate_expr(e))
            wln(fd, ") ")
            generate_seq_block(fd, s.stmts, indent + 2)
        elif isinstance(s, hdltree.HDLSync):
            w(fd, sindent)
            if s.name is not None:
                w(fd, '{}: '.format(s.name))
            w(fd, "always @(posedge({})".format(generate_expr(s.clk)))
            if s.rst is not None:
                assert s.rst_val == 0
                w(fd, " or negedge({})".format(generate_expr(s.rst)))
            wln(fd, ")")
            wln(fd, sindent + "begin")
            if s.rst is not None:
                wln(fd, sindent + "  if (!{})".format(generate_expr(s.rst)))
                generate_seq_block(fd, s.rst_stmts, indent + 2)
                wln(fd, sindent + "  else")
                generate_seq_block(fd, s.sync_stmts, indent + 2)
            else:
                generate_seq_block(fd, s.sync_stmts, indent + 2)
            wln(fd, sindent + "end")
        elif isinstance(s, hdltree.HDLInstance):
            w(fd, sindent + "{}".format(s.module_name))

            def generate_map(mapping, indent):
                first = True
                for p, e in mapping:
                    if first:
                        first = False
                    else:
                        wln(fd, ",")
                    w(fd, "  " * indent)
                    w(fd, "  .{}({})".format(p, generate_expr(e)))
                wln(fd)
            if s.params:
                wln(fd, " #(")
                generate_map(s.params, indent + 1)
                wln(fd, sindent + "  )")
            w(fd, sindent + "{}".format(s.name))
            if s.conns:
                wln(fd, " (")
                generate_map(s.conns, indent + 1)
                wln(fd, sindent + "  );")
            wln(fd, sindent)
        elif isinstance(s, hdltree.HDLGenIf):
            wln(fd, sindent + "genblock_{}: if ({}) generate".format(
                gen_num, generate_expr(s.cond)))
            generate_stmts(fd, s.stmts, indent + 1)
            wln(fd, sindent + "end generate genblock_{};".format(gen_num))
            gen_num += 1
        else:
            assert False, "unhandled hdl stmt {}".format(s)


def print_inters_list(fd, lst, name, indent):
    if not lst:
        return
    windent(fd, indent)
    wln(fd, "{}(".format(name))
    first = True
    for p in lst:
        if first:
            first = False
        else:
            wln(fd, ",")
        if isinstance(p, hdltree.HDLPort):
            generate_port(fd, p, indent + 1)
        elif isinstance(p, hdltree.HDLParam):
            generate_param(fd, p, indent + 1)
        elif isinstance(p, hdltree.HDLPortGroup):
            generate_decl_comment(fd, p.comment, indent + 1)
            group_typename = '{}.{}'.format(
                p.interface.name, 'master' if p.is_master else 'slave')
            windent(fd, indent + 1)
            w(fd, "{} {}".format(group_typename, p.name))
        else:
            raise AssertionError
    wln(fd)
    windent(fd, indent)
    wln(fd, ");")


def rename_interface_port(p):
    dirname = {'IN': 'i', 'OUT': 'o'}
    p.name = "{}{}".format(p.name, dirname[p.dir])


def extract_reg_init(decls):
    for d in decls:
        if isinstance(d, (hdltree.HDLSignal, hdltree.HDLPort)):
            d.p_vlg_reg = None
        elif isinstance(d, hdltree.HDLPortGroup):
            # Renames ports which have the same name
            names = {}
            for p in d.interface.ports:
                prev = names.get(p.name)
                if prev is not None:
                    # This is a duplicate
                    rename_interface_port(p)
                    rename_interface_port(prev)
                else:
                    names[p.name] = p


def extract_reg_assign(stmt, is_reg):
    targ = stmt.target
    while isinstance(targ, hdltree.HDLSlice) \
           or isinstance(targ, hdltree.HDLIndex):
        targ = targ.prefix
    if isinstance(targ, hdltree.HDLInterfaceSelect):
        return
    if isinstance(targ, hdltree.HDLInterface):
        return
    if targ.p_vlg_reg is None:
        targ.p_vlg_reg = is_reg
    elif targ.p_vlg_reg != is_reg:
        # Mismatch
        raise AssertionError(targ)


def extract_reg_seq(stmts):
    if stmts is None:
        return
    for s in stmts:
        if isinstance(s, hdltree.HDLAssign):
            extract_reg_assign(s, True)
        elif isinstance(s, hdltree.HDLIfElse):
            extract_reg_seq(s.then_stmts)
            extract_reg_seq(s.else_stmts)
        elif isinstance(s, hdltree.HDLSwitch):
            for c in s.choices:
                extract_reg_seq(c.stmts)
        elif isinstance(s, hdltree.HDLComment):
            pass
        else:
            raise AssertionError(s)


def extract_reg_module(module):
    "Detect whether ports/signals are wire or reg."
    extract_reg_init(module.ports)
    extract_reg_init(module.decls)
    for s in module.stmts:
        if isinstance(s, hdltree.HDLAssign):
            extract_reg_assign(s, False)
        elif isinstance(s, hdltree.HDLSync):
            extract_reg_seq(s.rst_stmts)
            extract_reg_seq(s.sync_stmts)
        elif isinstance(s, hdltree.HDLComb):
            extract_reg_seq(s.stmts)


def print_module(fd, module):
    extract_reg_module(module)
    if module.global_decls:
        for s in module.global_decls:
            generate_decl(fd, s, 1)
        wln(fd)

    generate_header(fd, module)
    wln(fd)
    wln(fd, "module {}".format(module.name))
    print_inters_list(fd, module.params, "#", 1)
    print_inters_list(fd, module.ports, "", 1)
    for s in module.decls:
        generate_decl(fd, s, 1)
    generate_stmts(fd, module.stmts, 1)
    wln(fd, "endmodule")


def print_verilog(fd, n):
    if isinstance(n, hdltree.HDLModule):
        print_module(fd, n)
    else:
        raise AssertionError

"""Print as a C structure."""
import cheby.tree as tree
import cheby.print_consts as print_consts


class CPrinter(tree.Visitor):
    def __init__(self, style):
        self.buffer = ''
        self.submaps = []
        self.indent = 0
        assert style in ['neutral', 'arm']
        self.style = style
        self.utypes = {1: 'uint8_t',
                       2: 'uint16_t',
                       4: 'uint32_t',
                       8: 'uint64_t'}
        self.stypes = {1: 'int8_t',
                       2: 'int16_t',
                       4: 'int32_t',
                       8: 'int64_t'}
        self.ftypes = {4: 'float',
                       8: 'double'}
        self.access = {'ro': ['__IM', 'volatile const'],
                       'rw': ['__IOM', 'volatile'],
                       'wo': ['__OM', 'volatile']}

    def cp_raw(self, s):
        self.buffer += s

    def inc(self):
        self.indent += 1

    def dec(self):
        self.indent -= 1

    def start_struct(self, name):
        self.cp_raw('{}struct {} {{\n'.format(
            '  ' * self.indent, name))
        self.inc()

    def end_struct(self, name):
        self.dec()
        if name is None:
            self.cp_txt('};')
        else:
            self.cp_txt('}} {};'.format(name))

    def cp_txt(self, txt):
        if txt:
            self.cp_raw('{}{}'.format('  ' * self.indent, txt))
        self.cp_raw('\n')


def cprint_children(cp, n, size):
    "Generate declarations for children of :param n:, and pad to :param size:"
    addr = 0
    pad_id = [0]  # Modified in the nested maybe_pad function

    def maybe_pad(diff):
        if diff == 0:
            return
        # Pad
        # Note: the 4 is not related to bus size, but to C types.
        if addr % 4 == 0 and diff % 4 == 0:
            sz = 4
        else:
            sz = 1
        cp.cp_txt('')
        cp.cp_txt('/* padding to: {} words */'.format(el.c_address // sz))
        cp.cp_txt('{} __padding_{}[{}];'.format(
            cp.utypes[sz], pad_id[0], diff // sz))
        pad_id[0] += 1

    for i in range(len(n.c_sorted_children)):
        el = n.c_sorted_children[i]
        diff = el.c_address - addr
        assert diff >= 0
        maybe_pad(diff)
        if i != 0:
            cp.cp_txt('')
        cp.visit(el)
        if isinstance(el, tree.Submap) and el.filename is not None:
            # Boxed instance.  There might be a difference of size
            # between the real submap and how much memory is used
            # in this map.
            addr = el.c_address + el.c_submap.c_size
        else:
            if isinstance(el, tree.Repeat):
                # There might be a gap between the size of the repeat block,
                # and the size of the element * count.
                rep_size = el.c_elsize * el.count
                addr = el.c_address + rep_size
                maybe_pad(el.c_size - rep_size)
            elif isinstance(el, tree.Memory):
                # Likewise.
                addr = el.c_address + el.memsize_val
                maybe_pad(el.c_size - el.memsize_val)
            addr = el.c_address + el.c_size
    # Last pad
    maybe_pad(size - addr)


@CPrinter.register(tree.Reg)
def cprint_reg(cp, n):
    cp.cp_txt('/* [0x{:x}]: REG ({}) {} */'.format(
        n.c_address, n.access, n.description or '(no description)'))
    if n.c_type == 'signed':
        typ = cp.stypes[n.c_size]
    elif n.c_type == 'float':
        typ = cp.ftypes[n.c_size]
    else:
        typ = cp.utypes[n.c_size]
    if cp.style == 'arm':
        acc = cp.access[n.access][0]
        cp.cp_txt('{} {} {};'.format(acc, typ, n.name))
    else:
        cp.cp_txt('{} {};'.format(typ, n.name))


@CPrinter.register(tree.Block)
def cprint_block(cp, n):
    cp.cp_txt('/* [0x{:x}]: BLOCK {} */'.format(
        n.c_address, n.description or '(no description)'))
    cp.start_struct(n.name)
    cprint_children(cp, n, n.c_size)
    cp.end_struct(n.name)


@CPrinter.register(tree.Memory)
def cprint_memory(cp, n):
    cp.cp_txt('/* [0x{:x}]: MEMORY {} */'.format(
        n.c_address, n.description or '(no description)'))
    cp.start_struct(n.name)
    cprint_children(cp, n, n.c_elsize)
    cp.end_struct('{}[{}]'.format(n.name, n.memsize_val // n.c_elsize))


@CPrinter.register(tree.Repeat)
def cprint_repeat(cp, n):
    cp.cp_txt('/* [0x{:x}]: REPEAT {} */'.format(
        n.c_address, n.description or '(no description)'))
    cp.start_struct(n.name)
    cprint_children(cp, n, n.c_elsize)
    cp.end_struct('{}[{}]'.format(n.name, n.count))


@CPrinter.register(tree.Submap)
def cprint_submap(cp, n):
    cp.cp_txt('/* [0x{:x}]: SUBMAP {} */'.format(
        n.c_address, n.description or '(no description)'))
    if n.filename is None:
        # Should depend on bus size ?
        if n.c_size % 4 == 0:
            sz = 4
        else:
            sz = 1
        cp.cp_txt('{} {}[{}];'.format(cp.utypes[sz], n.name, n.c_size // sz))
    else:
        cp.cp_txt('struct {} {};'.format(n.c_submap.name, n.name))
        cp.submaps.append(n.c_submap)


@CPrinter.register(tree.CompositeNode)
def cprint_composite(cp, n):
    cprint_children(cp, n, n.c_size)


@CPrinter.register(tree.Root)
def cprint_root(cp, n):
    if n.version:
        cp.cp_txt("/* For {} version: {} */".format(n.name, n.version))
    cp.start_struct(n.name)
    cprint_composite(cp, n)
    cp.end_struct(None)


def to_cmacro(name):
    return "__CHEBY__{}__H__".format(name.upper())


def gen_c_cheby(fd, root, style):
    cp = CPrinter(style)
    cprint_root(cp, root)
    csym = to_cmacro(root.name)
    fd.write("#ifndef {}\n".format(csym))
    fd.write("#define {}\n".format(csym))

    submaps = set([n.name for n in cp.submaps])
    if submaps:
        fd.write('\n')
    for s in submaps:
        # Note: we assume the filename is the name of the memmap + h
        fd.write('#include "{}.h"\n'.format(s))

    if cp.style == 'arm':
        # Add definition of access macros
        fd.write('\n')
        for m in sorted(cp.access):
            acc = cp.access[m]
            fd.write("#ifndef {}\n".format(acc[0]))
            fd.write("  #define {} {}\n".format(acc[0], acc[1]))
            fd.write("#endif\n")

    print_consts.pconsts_for_gen_c(fd, root)
    fd.write('\n')

    fd.write(cp.buffer)
    fd.write('\n')
    fd.write("#endif /* {} */\n".format(csym))

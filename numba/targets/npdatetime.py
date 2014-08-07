"""
Implementation of operations on numpy timedelta64.
"""

from llvm.core import Type, Constant
import llvm.core as lc

from numba import npdatetime, types, typing, cgutils, utils
from numba.targets.imputils import (builtin, builtin_attr, implement,
                                    impl_attribute, impl_attribute_generic,
                                    iterator_impl, iternext_impl,
                                    struct_factory, type_factory)
from numba.typing import signature


TIMEDELTA64 = Type.int(64)
NAT = Constant.int(TIMEDELTA64, npdatetime.NAT)


@type_factory(types.NPTimedelta)
def llvm_timedelta_type(context, tp):
    return TIMEDELTA64


TIMEDELTA_BINOP_SIG = (types.Kind(types.NPTimedelta),) * 2

def scale_timedelta(context, builder, val, srcty, destty):
    factor = npdatetime.get_timedelta_conversion_factor(srcty.unit, destty.unit)
    return builder.mul(Constant.int(TIMEDELTA64, factor), val)


@builtin
@implement('+', *TIMEDELTA_BINOP_SIG)
def timedelta_add_impl(context, builder, sig, args):
    # XXX NaT support
    [va, vb] = args
    [ta, tb] = sig.args
    va = scale_timedelta(context, builder, va, ta, sig.return_type)
    vb = scale_timedelta(context, builder, vb, tb, sig.return_type)
    return builder.add(va, vb)
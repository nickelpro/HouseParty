from dataclasses import dataclass

import circt
from circt import ir
from circt.dialects import hw, comb, _ods_common as ods

from .grammar import HPModule


@dataclass
class ForwardRef:
  opIndex: int
  target: str


def populateNands(assigns, ops, isIntermediate):
  cTrue = hw.ConstantOp(ir.BoolAttr.get(True))

  class NandOp(comb.XorOp):
    def __init__(self, inputs):
      self.andOp = comb.AndOp(inputs)
      super().__init__((self.andOp, cTrue))

  unresolved = []  # Ops with forward refs
  for target, exprs in assigns.items():
    forwardRefs = []
    operands = []
    for idx, ident in enumerate(exprs):
      if ident in ops:
        operands.append(ops[ident])
      elif ident in assigns:
        operands.append(cTrue)
        forwardRefs.append(ForwardRef(idx, ident))
      else:
        raise RuntimeError(f'Unknown expression: {ident}')

    if len(operands) > 1:
      op = NandOp(operands)
    else:
      operands.append(cTrue)
      op = comb.XorOp(operands)

    if forwardRefs:
      t = op.andOp if len(operands) > 1 else op
      unresolved.append((t, forwardRefs))

    if isIntermediate(target):
      op = hw.WireOp(op, name=target,
                     inner_sym=hw.InnerSymAttr.get(ir.StringAttr.get(target)))

    ops[target] = op

  return unresolved


def resolveForwardRefs(unresolved, ops):
  for op, fills in unresolved:
    for fill in fills:
      op.operands[fill.opIndex] = ods.get_op_result_or_value(ops[fill.target])


def genIR(hpmod: HPModule, use_int=True):
  with ir.Context() as ctx, ir.Location.unknown():
    circt.register_dialects(ctx)
    irmod = ir.Module.create()
    i1 = ir.IntegerType.get_signless(1)

    with ir.InsertionPoint(irmod.body):

      def genBody(module):
        if use_int:
          isInt = lambda x: x not in hpmod.inputs and x not in hpmod.outputs
        else:
          isInt = lambda _: False

        ops = module.inputs()
        assigns = hpmod.assigns.copy()
        unresolved = populateNands(assigns, ops, isInt)
        resolveForwardRefs(unresolved, ops)

        return {ident: ops[ident] for ident in hpmod.outputs}

      hw.HWModuleOp(
          name=hpmod.ident,
          input_ports=[(ident, i1) for ident in hpmod.inputs],
          output_ports=[(ident, i1) for ident in hpmod.outputs],
          body_builder=genBody,
      )

  return irmod

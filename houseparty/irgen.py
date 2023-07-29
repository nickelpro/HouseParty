import typing
from dataclasses import dataclass

import circt
from circt import ir
from circt.dialects import hw, comb, _ods_common as ods

from .grammar import HPModule


@dataclass
class Resolution:
  opIndex: int
  target: str


class IntermediateWire(hw.WireOp):
  def __init__(self, input, name):
    operands = [ods.get_op_result_or_value(input)]
    results = [operands[0].type]
    attributes = {
        'name': ir.StringAttr.get(name),
        'inner_sym': ir.StringAttr.get(name),
    }
    super().__init__(
        self.build_generic(attributes=attributes, results=results,
                           operands=operands))


def genIR(hpmod: HPModule, use_int=True):
  with ir.Context() as ctx, ir.Location.unknown():
    circt.register_dialects(ctx)
    irmod = ir.Module.create()
    i1 = ir.IntegerType.get_signless(1)

    with ir.InsertionPoint(irmod.body):

      def genBody(module):
        cTrue = hw.ConstantOp(ir.BoolAttr.get(True))

        class NandOp(comb.XorOp):
          def __init__(self, inputs):
            self.andOp = comb.AndOp(inputs)
            super().__init__((self.andOp, cTrue))

        def isIntermediate(target):
          return target not in hpmod.inputs and target not in hpmod.outputs

        ops = module.inputs()
        assigns = hpmod.assigns.copy()
        unresolved = []

        for target, exprs in assigns.items():
          opUnresolved = []
          operands = []
          for idx, ident in enumerate(exprs):
            if ident in ops:
              operands.append(ops[ident])
            elif ident in assigns:
              operands.append(cTrue)
              opUnresolved.append(Resolution(idx, ident))
            else:
              RuntimeError(f'Unknown expression: {ident}')

          op = NandOp(operands) if len(operands) > 1 else comb.XorOp(operands)

          if opUnresolved:
            t = op.andOp if len(operands) > 1 else op
            unresolved.append((t, opUnresolved))

          if use_int and isIntermediate(target):
            op = IntermediateWire(op, target)

          ops[target] = op

        for op, fills in unresolved:
          for fill in fills:
            op.operands[fill.opIndex] = ods.get_op_result_or_value(
                ops[fill.target])

        return {ident: ops[ident] for ident in hpmod.outputs}

      hw.HWModuleOp(
          name=hpmod.ident,
          input_ports=[(ident, i1) for ident in hpmod.inputs],
          output_ports=[(ident, i1) for ident in hpmod.outputs],
          body_builder=genBody,
      )

  return irmod

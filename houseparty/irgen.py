import circt
from circt import ir
from circt.dialects import hw, comb, _ods_common as ods

from .grammar import HPModule


class IntermediateWire(hw.WireOp):
  def __init__(self, input, name, inner_sym):
    operands = [ods.get_op_result_or_value(input)]
    results = [operands[0].type]
    attributes = {
        'name': ir.StringAttr.get(name),
        'inner_sym': ir.StringAttr.get(inner_sym),
    }
    super().__init__(
        self.build_generic(attributes=attributes, results=results,
                           operands=operands))


def genIR(hpmod: HPModule):
  with ir.Context() as ctx, ir.Location.unknown():
    circt.register_dialects(ctx)
    irmod = ir.Module.create()
    i1 = ir.IntegerType.get_signless(1)

    with ir.InsertionPoint(irmod.body):

      def genBody(module):
        cTrue = hw.ConstantOp(ir.BoolAttr.get(True))

        def isIntermediate(target):
          return target not in hpmod.inputs and target not in hpmod.outputs

        def resolve(target, expr, assigns, ops):
          for ident in expr:
            if ident in ops:
              continue
            elif ident in assigns:
              expr = assigns.pop(ident)
              resolve(ident, expr, assigns, ops)
            else:
              raise RuntimeError(f'Unknown expression: {ident}')

          if (len(expr) > 1):
            andOp = comb.AndOp([ops[ident] for ident in expr])
            xorOp = comb.XorOp((andOp, cTrue))
          else:
            xorOp = comb.XorOp((ops[expr[0]], cTrue))

          if isIntermediate(target):
            ops[target] = IntermediateWire(xorOp, target, target)
          else:
            ops[target] = xorOp

        ops = module.inputs()
        assigns = hpmod.assigns.copy()

        while assigns:
          target, expr = assigns.popitem()
          resolve(target, expr, assigns, ops)

        out = {}
        for ident, op in ops.items():
          if ident in hpmod.outputs:
            out[ident] = op

        return out

      hw.HWModuleOp(
          name=hpmod.ident,
          input_ports=[(ident, i1) for ident in hpmod.inputs],
          output_ports=[(ident, i1) for ident in hpmod.outputs],
          body_builder=genBody,
      )

  return irmod

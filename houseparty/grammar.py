from dataclasses import dataclass
import pyparsing as pp


@dataclass
class IdentBase:
  ident: str

  @classmethod
  def parseAction(cls, tokens: pp.ParseResults):
    return cls(tokens[1])


identWord = pp.Word(pp.identchars, pp.identbodychars, as_keyword=True)


def createIdentDecl(clsName: str, ident: str):
  cls = dataclass(type(clsName, (IdentBase, ), {}))
  decl = pp.Keyword(ident) + identWord + pp.LineEnd()
  decl.set_parse_action(cls.parseAction)
  return cls, decl


HPModDecl, moduleDecl = createIdentDecl("HPModDecl", "houseparty")
HPInputDecl, inputDecl = createIdentDecl("HPInputDecl", "sup")
HPOutputDecl, outputDecl = createIdentDecl("HPOutputDecl", "outtahere")


@dataclass
class HPAssignment:
  target: str
  expr: list[str]

  @staticmethod
  def parseAction(tokens: pp.ParseResults):
    return HPAssignment(tokens[0], tokens[2:])


assignStmnt = identWord + pp.Keyword("knows") + identWord[1, ...:pp.LineEnd()]
assignStmnt.set_parse_action(HPAssignment.parseAction)


@dataclass
class HPModule:
  ident: str
  inputs: list[str]
  outputs: list[str]
  assigns: dict[str, str]

  @staticmethod
  def parseAction(tokens: pp.ParseResults):
    modName = tokens[0].ident
    inputs = []
    outputs = []
    assigns = {}
    for tok in tokens[1:]:
      match tok:
        case HPInputDecl(ident):
          inputs.append(ident)
        case HPOutputDecl(ident):
          outputs.append(ident)
        case HPAssignment(target, expr):
          assigns[target] = expr
    return HPModule(modName, inputs, outputs, assigns)


bodyLine = inputDecl | outputDecl | assignStmnt
modGrammar = moduleDecl + bodyLine[...] + pp.Keyword("cops!")
modGrammar.set_parse_action(HPModule.parseAction)


def readFile(filename) -> HPModule:
  return modGrammar.parse_file(filename)[0]

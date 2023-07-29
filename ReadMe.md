# 🎉 HouseParty 🎉

An esoteric HDL I wrote to learn a little about CIRCT

Example:

```
houseparty DFlipFlop

  sup clk
  sup D

  D_Prime knows clk D
  E_Prime knows clk D_Prime

  Q       knows D_Prime Q_Prime
  Q_Prime knows E_Prime Q

  outtahere Q
  outtahere Q_Prime

cops!
```

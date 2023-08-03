#include <catch2/catch_test_macros.hpp>
#include <NyuTestUtil.hpp>

#include <HPDFlipFlop.h>

TEST_CASE("DFlipFlop")
{
  auto &ff{nyu::getDUT<HPDFlipFlop>()};
  nyu::tracer trace{ff, "flipflop.fst"};

  ff.D = 0;
  ff.clk = 1;
  nyu::eval(trace);

  REQUIRE(ff.Q == 0);
  REQUIRE(ff.Q_Prime == 1);

  ff.clk = 0;
  nyu::eval(trace);

  ff.D = 1;
  nyu::eval(trace);

  ff.D = 0;
  nyu::eval(trace);

  ff.D = 1;
  nyu::eval(trace);

  ff.clk = 1;
  nyu::eval(trace, 2);

  REQUIRE(ff.Q == 1);
  REQUIRE(ff.Q_Prime == 0);
}

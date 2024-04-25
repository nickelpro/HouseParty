#include <catch2/catch_test_macros.hpp>
#include <NyuTestUtil.hpp>

#include <HPDFlipFlop.h>

TEST_CASE("DFlipFlop") {
  auto& ff {nyu::getDUT<HPDFlipFlop>()};

  ff.D = 0;
  ff.clk = 1;
  nyu::eval(ff);

  REQUIRE(ff.Q == 0);
  REQUIRE(ff.Q_Prime == 1);

  ff.clk = 0;
  nyu::eval(ff);

  ff.D = 1;
  nyu::eval(ff);

  ff.D = 0;
  nyu::eval(ff);

  ff.D = 1;
  nyu::eval(ff);

  ff.clk = 1;
  nyu::eval(ff, 2);

  REQUIRE(ff.Q == 1);
  REQUIRE(ff.Q_Prime == 0);
}

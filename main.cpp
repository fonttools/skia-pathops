#include <SkPath.h>
#include <SkPathOps.h>

int
main(int argc, char** argv)
{
  SkOpBuilder builder;
  SkPath path1, path2, result;

  path1.moveTo(5, -225);
  path1.lineTo(-225, 7425);
  path1.lineTo(7425, 7425);
  path1.lineTo(7425, -225);
  path1.lineTo(-225, -225);
  path1.lineTo(5, -225);
  path1.close();

  path2.moveTo(5940, 2790);
  path2.lineTo(5940, 2160);
  path2.lineTo(5970, 1980);
  path2.lineTo(5688, 773669888);
  path2.lineTo(5688, 2160);
  path2.lineTo(5688, 2430);
  path2.lineTo(5400, 4590);
  path2.lineTo(5220, 4590);
  path2.lineTo(5220, 4920);
  path2.cubicTo(5182.22900390625f, 4948.328125f, 5160, 4992.78662109375f, 5160, 5040.00048828125f);
  path2.lineTo(5940, 2790);
  path2.close();

  builder.add(path1, kUnion_SkPathOp);
  builder.add(path2, kUnion_SkPathOp);
  bool ok = builder.resolve(&result);

  if (ok)
  {
    SkPath::Iter iter(result, false);
    SkPoint p[4];
    SkPath::Verb verb;

    while ((verb = iter.next(p, false)) != SkPath::kDone_Verb) {
      switch (verb) {
        case SkPath::kMove_Verb:
          printf("moveTo (%g, %g)", p[0].x(), p[0].y());
          break;
        case SkPath::kLine_Verb:
          printf("lineTo (%g, %g)", p[1].x(), p[1].y());
          break;
        case SkPath::kQuad_Verb:
          printf("quadTo (%g, %g) (%g, %g)", p[1].x(), p[1].y(), p[2].x(), p[2].y());
          break;
        case SkPath::kConic_Verb:
          printf("conicTo (%g, %g) (%g, %g) (%g)", p[1].x(), p[1].y(), p[2].x(), p[2].y(), iter.conicWeight());
          break;
        case SkPath::kCubic_Verb:
          printf("cubicTo (%g, %g) (%g, %g) (%g, %g)", p[1].x(), p[1].y(), p[2].x(), p[2].y(), p[3].x(), p[3].y());
          break;
        case SkPath::kClose_Verb:
          printf("close");
          break;
        case SkPath::kDone_Verb:
          break;
      }
      printf("\n");
    }
  }

  return !ok;
}

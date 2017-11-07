NULL =

OBJS = \
       skia/src/core/SkArenaAlloc.o \
       skia/src/core/SkBuffer.o \
       skia/src/core/SkCubicClipper.o \
       skia/src/core/SkData.o \
       skia/src/core/SkGeometry.o \
       skia/src/core/SkMath.o \
       skia/src/core/SkMatrix.o \
       skia/src/core/SkPath.o \
       skia/src/core/SkPathRef.o \
       skia/src/core/SkPoint.o \
       skia/src/core/SkRect.o \
       skia/src/core/SkRRect.o \
       skia/src/core/SkSemaphore.o \
       skia/src/core/SkString.o \
       skia/src/core/SkStringUtils.o \
       skia/src/core/SkUtils.o \
       skia/src/core/SkThreadID.o \
       skia/src/pathops/SkAddIntersections.o \
       skia/src/pathops/SkDConicLineIntersection.o \
       skia/src/pathops/SkDCubicLineIntersection.o \
       skia/src/pathops/SkDCubicToQuads.o \
       skia/src/pathops/SkDLineIntersection.o \
       skia/src/pathops/SkDQuadLineIntersection.o \
       skia/src/pathops/SkIntersections.o \
       skia/src/pathops/SkOpAngle.o \
       skia/src/pathops/SkOpBuilder.o \
       skia/src/pathops/SkOpCoincidence.o \
       skia/src/pathops/SkOpContour.o \
       skia/src/pathops/SkOpCubicHull.o \
       skia/src/pathops/SkOpEdgeBuilder.o \
       skia/src/pathops/SkOpSegment.o \
       skia/src/pathops/SkOpSpan.o \
       skia/src/pathops/SkPathOpsCommon.o \
       skia/src/pathops/SkPathOpsConic.o \
       skia/src/pathops/SkPathOpsCubic.o \
       skia/src/pathops/SkPathOpsCurve.o \
       skia/src/pathops/SkPathOpsDebug.o \
       skia/src/pathops/SkPathOpsLine.o \
       skia/src/pathops/SkPathOpsOp.o \
       skia/src/pathops/SkPathOpsPoint.o \
       skia/src/pathops/SkPathOpsQuad.o \
       skia/src/pathops/SkPathOpsRect.o \
       skia/src/pathops/SkPathOpsSimplify.o \
       skia/src/pathops/SkPathOpsTightBounds.o \
       skia/src/pathops/SkPathOpsTSect.o \
       skia/src/pathops/SkPathOpsTypes.o \
       skia/src/pathops/SkPathOpsWinding.o \
       skia/src/pathops/SkPathWriter.o \
       skia/src/pathops/SkReduceOrder.o \
       skia/src/ports/SkDebug_stdio.o \
       skia/src/ports/SkMemory_malloc.o \
       skia/src/ports/SkOSFile_posix.o \
       skia/src/ports/SkOSFile_stdio.o \
       $(NULL)

LDLIBS = \
       -lm \
       -lpthread \
       $(NULL)

CXXFLAGS = \
       -I./skia/include/config \
       -I./skia/include/core \
       -I./skia/include/pathops \
       -I./skia/include/private \
       -I./skia/src/core \
       -I./skia/src/opts \
       -I./skia/src/shaders \
       -Wall \
       $(NULL)

main: main.o $(OBJS)
	$(CXX) $+ $(LDFLAGS) $(LDLIBS) -o $@

clean:
	rm -rf $(OBJS) main.o main

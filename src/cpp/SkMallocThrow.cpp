// This is to avoid importing src/core/SkMallocPixelRef.cpp (which implements
// among other things the `sk_malloc_throw` function below), as the latter
// has a long list of dependencies which we don't need for skia-pathops.
// The function is used by SkTArray.h, included by pathops/SkPathWriter.h.
#include "include/private/SkMalloc.h"
#include "src/core/SkSafeMath.h"

void* sk_malloc_throw(size_t count, size_t elemSize) {
    return sk_malloc_throw(SkSafeMath::Mul(count, elemSize));
}

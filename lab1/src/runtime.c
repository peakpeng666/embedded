#include <stddef.h>

/* GCC may emit this even for a C aggregate initializer in a freestanding build. */
void *memset(void *destination, int value, size_t count)
{
    volatile unsigned char *cursor = destination;
    while (count != 0u) {
        *cursor++ = (unsigned char)value;
        count--;
    }
    return destination;
}

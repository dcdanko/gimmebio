#include <inttypes.h>
#include <Python.h>

uint64_t nextRabinFingerprint( uint64_t oldHash, uint8_t oldBase, uint8_t newBase, uint8_t power, uint8_t radix);

PyObject * rabinFingerprints(char * seq, uint8_t seqLen, uint8_t power, uint8_t radix);
  
uint8_t baseToInt(char base);

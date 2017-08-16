#include "ckmers.h"
#include <math.h>
#include <stdio.h>
#include <Python.h>

uint64_t nextRabinFingerprint( uint64_t oldHash, uint8_t oldBase, uint8_t newBase, uint8_t power, uint8_t radix){
  return radix * (oldHash - (oldBase * (radix << power))) + newBase;
}

uint8_t baseToInt(char base){
  switch(base){
  case 'A':
    return 0;
  case 'C':
    return 1;
  case 'G':
    return 2;
  case 'T':
    return 3;
  default:
    return 4;
  }
}

PyObject * rabinFingerprints(char * seq, uint8_t seqLen, uint8_t power, uint8_t radix){
  uint8_t useq[seqLen];
  int i, k;
  uint64_t initHash;
  for(i=0; i<seqLen; i++){
    useq[i] = baseToInt( seq[i]);
  }


  k = 1 + pow(2, power);
  initHash = 0;
  uint64_t allHash[seqLen - k + 1];
  for(i=0; i<k; i++){
    initHash += useq[i] * pow(radix, (k - 1 - i));
  }
  allHash[0] = initHash;

  for(i=k; i<seqLen; i++){
    allHash[i - k + 1] = nextRabinFingerprint( allHash[i - k],
					       useq[i - k],
					       useq[i],
					       power,
					       radix);

  }

  PyObject * ret = PyList_New(seqLen - k + 1);
  for(i=0; i<(seqLen - k + 1); i++){
    PyList_SET_ITEM(ret, i, PyLong_FromLongLong( allHash[i]));
  }
  return ret;
}
  
  

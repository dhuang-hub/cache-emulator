#!/bin/bash

#RESDIR="analysis_results/"
RESDIR="./"


echo "Associativity Analysis" > "${RESDIR}associativity_analysis.txt"
for n in 1 2 4 8 16 1024
do
  echo >> "${RESDIR}associativity_analysis.txt"
  echo >> "${RESDIR}associativity_analysis.txt"
  echo "Associativity: ${n}" >> "${RESDIR}associativity_analysis.txt"
  python cache-sim.py -n "$n" >> "${RESDIR}associativity_analysis.txt"
done


echo "Memory Block Analysis" > "${RESDIR}memory_block_analysis.txt"
for b in 8 16 32 64 128 256 512 1024
do
  echo >> "${RESDIR}memory_block_analysis.txt"
  echo >> "${RESDIR}memory_block_analysis.txt"
  echo "Memory Block Size: ${b}" >> "${RESDIR}memory_block_analysis.txt"
  python cache-sim.py -b "$b" >> "${RESDIR}memory_block_analysis.txt"
done


echo "Cache Size Analysis" > "${RESDIR}cache_size_analysis.txt"
for c in 4096 8192 16384 32768 65536 131072 262144 524288
do
  echo >> "${RESDIR}cache_size_analysis.txt"
  echo >> "${RESDIR}cache_size_analysis.txt"
  echo "Total Cache Size: ${c}" >> "${RESDIR}cache_size_analysis.txt"
  python cache-sim.py -c "$c" >> "${RESDIR}cache_size_analysis.txt"
done


echo "Matrix Multiply Analysis" > "${RESDIR}mxm_analysis.txt"
for n in 2 8 1024
do
  for i in 480,32 488,8 512,32
  do
    IFS=',' read d f <<< "${i}";
    for a in "mxm" "mxm_block"
    do
      echo >> "${RESDIR}mxm_analysis.txt"
      echo >> "${RESDIR}mxm_analysis.txt"
      echo "Matrix Multiply: ${n} Associativity / ${d} Dimension / ${a} Method / ${f} BlockFactor"  >> "${RESDIR}mxm_analysis.txt"
      python cache-sim.py -n "$n" -d "$d" -a "$a" -f "$f" >> "${RESDIR}mxm_analysis.txt"
    done
  done
done

echo "Replacement Policy Analysis" > "${RESDIR}replacement_analysis.txt"
for i in "daxpy",10000000 "mxm",480 "mxm_block",480
do
  IFS=',' read a d <<< "${i}";
  for r in "random" "FIFO" "LRU"
  do
    echo >> "${RESDIR}replacement_analysis.txt"
    echo >> "${RESDIR}replacement_analysis.txt"
    echo "Replacement Strategy: ${r} for ${a}" >> "${RESDIR}replacement_analysis.txt"
    python cache-sim.py -a "$a" -d "$d" -r "$r" >> "${RESDIR}replacement_analysis.txt"
  done
done

echo "Skylake Associativity Analysis" > "${RESDIR}skylake_associativity_analysis.txt"
for n in 2 4 8 16 32
do
  echo >> "${RESDIR}skylake_associativity_analysis.txt"
  echo >> "${RESDIR}skylake_associativity_analysis.txt"
  echo "Skylake Associativity: ${n}" >> "${RESDIR}skylake_associativity_analysis.txt"
  python cache-sim.py -c "32768" -n "$n" >> "${RESDIR}skylake_associativity_analysis.txt"
done
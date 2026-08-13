#!/bin/bash
set -euxo pipefail

python3 -m pip install "$SRC/memdevice-bench"

for fuzzer in "$SRC"/memdevice-bench/fuzzers/*_fuzzer.py; do
  fuzzer_basename=$(basename -s .py "$fuzzer")
  fuzzer_package="${fuzzer_basename}.pkg"

  pyinstaller --distpath "$OUT" --onefile --name "$fuzzer_package" "$fuzzer"
  printf '%s\n' \
    '#!/bin/sh' \
    'this_dir=$(dirname "$0")' \
    'LD_PRELOAD="$this_dir/sanitizer_with_fuzzer.so" \' \
    'ASAN_OPTIONS="$ASAN_OPTIONS:symbolize=1:external_symbolizer_path=$this_dir/llvm-symbolizer:detect_leaks=0" \' \
    "exec \"\$this_dir/$fuzzer_package\" \"\$@\"" \
    > "$OUT/$fuzzer_basename"
  chmod +x "$OUT/$fuzzer_basename"
done

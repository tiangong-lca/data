#!/bin/sh
set -eu

# Build the published 0.1.9 source with the narrowly scoped rev-list stdin fix.
# The source, lockfile, patch, and resulting Git module are verified before use.
repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
source_commit="d07ba8c500c6a10d90edfd7fb062018d2d3cbf96"
source_url="${DOCPACT_SOURCE_URL:-https://github.com/Biaoo/docpact.git}"
patch_path="$repo_root/scripts/patches/docpact-0.1.9-rev-list-stdin.patch"
build_parent="${DOCPACT_BUILD_PARENT:-${RUNNER_TEMP:-${TMPDIR:-/tmp}}}"

file_sha256() {
  if command -v sha256sum >/dev/null 2>&1; then
    digest="$(sha256sum "$1")"
  elif command -v shasum >/dev/null 2>&1; then
    digest="$(shasum -a 256 "$1")"
  else
    echo "A SHA-256 command is required (sha256sum or shasum)." >&2
    return 127
  fi
  printf '%s\n' "${digest%% *}"
}

verify_sha256() {
  expected="$1"
  path="$2"
  actual="$(file_sha256 "$path")"
  if [ "$actual" != "$expected" ]; then
    echo "SHA-256 mismatch for $path: expected $expected, got $actual" >&2
    return 1
  fi
}

verify_sha256 \
  "d4a1a3c043c1c99830930986c7bfc6f5f883d21ee945ed140d4749f8a5b017d7" \
  "$patch_path"

mkdir -p "$build_parent"
source_dir="$(mktemp -d "$build_parent/docpact-0.1.9.XXXXXX")"
git clone --quiet --no-checkout "$source_url" "$source_dir"
git -C "$source_dir" checkout --quiet --detach "$source_commit"

if [ "$(git -C "$source_dir" rev-parse HEAD)" != "$source_commit" ]; then
  echo "Docpact source commit does not match the pinned v0.1.9 commit." >&2
  exit 1
fi

verify_sha256 \
  "15a2aa5d046ef3b63652916a681dfc2ca271afa034baf3b71fb5e408fa43b8b6" \
  "$source_dir/src/git/mod.rs"
verify_sha256 \
  "ecc7dd16e96c95133a39d4892750c9ed8aba96de1952829568f450113118cb71" \
  "$source_dir/Cargo.lock"

git -C "$source_dir" apply --unidiff-zero --check "$patch_path"
git -C "$source_dir" apply --unidiff-zero "$patch_path"
git -C "$source_dir" diff --check
verify_sha256 \
  "f3aa8874cf76fedb5eaa75bc1cc7125520b5a4005924952c622ffe87c013ee9a" \
  "$source_dir/src/git/mod.rs"

export CARGO_TARGET_DIR="$source_dir/target"
cargo test --locked --manifest-path "$source_dir/Cargo.toml" --quiet >&2
cargo build --locked --release --manifest-path "$source_dir/Cargo.toml" --quiet >&2

docpact_bin="$CARGO_TARGET_DIR/release/docpact"
if [ "$("$docpact_bin" --version)" != "docpact 0.1.9" ]; then
  echo "Built Docpact binary did not report version 0.1.9." >&2
  exit 1
fi

printf '%s\n' "$docpact_bin"

#!/bin/bash
set -eu
target=$1
directory=$2
python=${BATTEN_GATE_PYTHON:-python3}
unset PYTHONPATH PYTHONHOME PYTHONOPTIMIZE
export PYTHONNOUSERSITE=1
if [ -e "$directory" ] || [ -L "$directory" ]; then
    echo "CI receipt directory already exists" >&2
    exit 2
fi
cleanup() {
    "$python" -c 'import shutil,sys; from pathlib import Path
root = Path(sys.argv[1])
packet = root / "20261111"
if packet.is_dir():
    shutil.rmtree(packet)
(root / "packet.tar.gz").unlink(missing_ok=True)' "$directory"
}
trap cleanup EXIT
"$python" scripts/note_task_gate/prepare_ci.py "$directory"
args=()
case "$target" in
    verify|linux) ;;
    macos)
        args+=(--uv "${BATTEN_GATE_UV:?Set the pinned uv executable path}"
               --pg-bin "${BATTEN_GATE_PG_BIN:-/opt/homebrew/bin}")
        ;;
    apps)
        args+=(--profile aidev-cus --app "${BATTEN_DATABRICKS_APP:?Set the dedicated qualification app}"
               --workspace-host "${BATTEN_DATABRICKS_HOST:?Set the workspace host}"
               --workspace-id "${BATTEN_DATABRICKS_WORKSPACE_ID:?Set the workspace ID}")
        ;;
    workers)
        args+=(--cloudflare-account "${CLOUDFLARE_ACCOUNT_ID:?Select the qualification account}")
        ;;
    *) echo "Unknown gate target" >&2; exit 2 ;;
esac
"$python" scripts/note_task_gate/gate.py "$target" \
    --packet "$directory/20261111" --receipt "$directory/receipt.json" ${args[@]+"${args[@]}"}

"""Convert a model's Blender actions into Roblox KeyframeSequence files.

Run with Blender (it bundles numpy and mathutils), from the repo root:

    blender -b blender/<Model>.blend --python scripts/export_animations.py -- \
        --rig <ArmatureName> --model <Model>

(--model is the model's key in scripts/rigs/roblox_rest.json.)
Writes blender/export/animations/<Model>_<Action>.rbxmx, which
scripts/upload_assets.py uploads as Animation assets.

How it works: Roblox animates a bone with Pose CFrames equal to Bone.Transform,
expressed in the Roblox bone's own frame. Those frames depend on how Roblox
imported the rig (and on any fix applied after import), so instead of assuming
an axis convention the script reads the bones' rest WorldCFrames from
scripts/rigs/roblox_rest.json (dumped from Studio), fits the rotation that maps
Blender armature space onto them from the bone head positions, then for every
frame moves each Roblox bone by the same world-space delta as its Blender bone
and solves for the local Transform. Re-dump roblox_rest.json when a model is
re-imported or its bones are changed.
"""

import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix

REPO = Path(__file__).resolve().parent.parent
REST_FILE = REPO / "scripts" / "rigs" / "roblox_rest.json"
OUT_DIR = REPO / "blender" / "export" / "animations"
# Default action names; pass --actions to export others. Actions not listed in
# PRIORITY export as Action priority; LOOPED marks looping ones. The game can
# override both at runtime when it plays the track.
ACTIONS = ("Idle", "Walk", "Attack", "Hit")
PRIORITY = {"Idle": 0, "Walk": 1, "Run": 1}
LOOPED = {"Idle", "Walk", "Run"}


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--rig", required=True, help="Blender armature object name")
    parser.add_argument("--model", required=True, help="entry in roblox_rest.json and file prefix")
    parser.add_argument("--actions", nargs="*", default=list(ACTIONS))
    parser.add_argument("--debug-json", help="also write the pose CFrames as JSON")
    return parser.parse_args(argv)


def cframe_to_matrix(c):
    """Roblox CFrame components (x, y, z, R00..R22, row-major) -> 4x4 numpy."""
    m = np.identity(4)
    m[0:3, 3] = c[0:3]
    m[0:3, 0:3] = np.array(c[3:12]).reshape(3, 3)
    return m


def matrix_to_cframe(m):
    # Re-orthonormalise so float drift never produces a skewed CFrame.
    u, _, vt = np.linalg.svd(m[0:3, 0:3])
    r = u @ vt
    return [float(v) for v in m[0:3, 3]] + [float(v) for v in r.reshape(9)]


def to_np(matrix: Matrix):
    return np.array([list(row) for row in matrix])


def fit_mapping(blender_points, roblox_points):
    """Rigid transform (rotation + translation) taking Blender points to Roblox (Kabsch)."""
    a = np.array(blender_points)
    b = np.array(roblox_points)
    ca, cb = a.mean(axis=0), b.mean(axis=0)
    u, _, vt = np.linalg.svd((a - ca).T @ (b - cb))
    d = np.sign(np.linalg.det(vt.T @ u.T))
    rotation = vt.T @ np.diag([1, 1, d]) @ u.T
    mapping = np.identity(4)
    mapping[0:3, 0:3] = rotation
    mapping[0:3, 3] = cb - rotation @ ca
    error = np.abs((rotation @ a.T).T + mapping[0:3, 3] - b).max()
    return mapping, error


def solve_poses(rest, deltas, mapping, order):
    """Pose CFrame (Bone.Transform) per bone for one frame."""
    inv_map = np.linalg.inv(mapping)
    part = cframe_to_matrix(rest["part"])
    rest_world = {name: cframe_to_matrix(b["w"]) for name, b in rest["bones"].items()}
    posed_world = {}
    for name in order:
        delta = mapping @ deltas[name] @ inv_map
        posed_world[name] = delta @ rest_world[name]
    poses = {}
    for name in order:
        parent = rest["bones"][name]["p"]
        parent_rest = rest_world[parent] if parent else part
        parent_posed = posed_world[parent] if parent else part
        local_rest = np.linalg.inv(parent_rest) @ rest_world[name]
        local_posed = np.linalg.inv(parent_posed) @ posed_world[name]
        poses[name] = np.linalg.inv(local_rest) @ local_posed
    return poses


def hierarchy_order(rest):
    order, pending = [], dict(rest["bones"])
    while pending:
        for name, bone in list(pending.items()):
            if not bone["p"] or bone["p"] in order:
                order.append(name)
                del pending[name]
    return order


class Xml:
    def __init__(self):
        self.lines = ['<roblox version="4">']
        self.ref = 0

    def open(self, cls):
        self.ref += 1
        self.lines.append(f'<Item class="{cls}" referent="RBX{self.ref}"><Properties>')

    def close_props(self):
        self.lines.append("</Properties>")

    def end(self):
        self.lines.append("</Item>")

    def prop(self, kind, name, value):
        self.lines.append(f'<{kind} name="{name}">{value}</{kind}>')

    def cframe(self, name, c):
        keys = ("X", "Y", "Z", "R00", "R01", "R02", "R10", "R11", "R12", "R20", "R21", "R22")
        inner = "".join(f"<{k}>{v:.7g}</{k}>" for k, v in zip(keys, c))
        self.lines.append(f'<CoordinateFrame name="{name}">{inner}</CoordinateFrame>')

    def text(self):
        return "\n".join(self.lines + ["</roblox>"]) + "\n"


def write_pose(xml, name, cframe, children):
    xml.open("Pose")
    xml.prop("string", "Name", name)
    xml.cframe("CFrame", cframe)
    xml.prop("token", "EasingDirection", 0)
    xml.prop("token", "EasingStyle", 0)  # Linear: every frame is baked
    xml.prop("float", "Weight", 1)
    xml.close_props()
    for child_name, child_cframe, grandchildren in children:
        write_pose(xml, child_name, child_cframe, grandchildren)
    xml.end()


def build_tree(name, poses, rest):
    kids = [n for n, b in rest["bones"].items() if b["p"] == name]
    return (name, matrix_to_cframe(poses[name]), [build_tree(k, poses, rest) for k in kids])


def main():
    args = parse_args()
    rest = json.loads(REST_FILE.read_text())[args.model]
    rig = bpy.data.objects[args.rig]
    scene = bpy.context.scene
    fps = scene.render.fps / scene.render.fps_base
    order = hierarchy_order(rest)
    missing = [n for n in order if n not in rig.data.bones]
    if missing:
        raise SystemExit(f"Roblox bones missing from {args.rig}: {missing}")
    skipped = [b.name for b in rig.data.bones if b.name not in rest["bones"]]

    arm_world = to_np(rig.matrix_world)
    rest_arm = {n: arm_world @ to_np(rig.data.bones[n].matrix_local) for n in order}
    mapping, error = fit_mapping(
        [rest_arm[n][0:3, 3] for n in order],
        [rest["bones"][n]["w"][0:3] for n in order],
    )
    print(f"[anim] {args.model}: mapping fitted from {len(order)} bones, max error {error:.4f} studs")
    if error > 0.02:
        raise SystemExit("Blender and Roblox rest poses do not match; re-dump roblox_rest.json")
    if skipped:
        print(f"[anim] Blender-only bones ignored (not in the Roblox rig): {skipped}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rig.animation_data_create()
    original_action = rig.animation_data.action
    debug = {}
    try:
        for action_name in args.actions:
            action = bpy.data.actions.get(action_name)
            if action is None:
                print(f"[anim] no action named {action_name}; skipped")
                continue
            rig.animation_data.action = action
            start, end = (int(round(f)) for f in action.frame_range)
            xml = Xml()
            xml.open("KeyframeSequence")
            xml.prop("string", "Name", action_name)
            xml.prop("bool", "Loop", "true" if action_name in LOOPED else "false")
            xml.prop("token", "Priority", PRIORITY.get(action_name, 2))
            xml.close_props()
            debug[action_name] = []
            for frame in range(start, end + 1):
                scene.frame_set(frame)
                deltas = {}
                for n in order:
                    posed = arm_world @ to_np(rig.pose.bones[n].matrix)
                    deltas[n] = posed @ np.linalg.inv(rest_arm[n])
                poses = solve_poses(rest, deltas, mapping, order)
                xml.open("Keyframe")
                xml.prop("string", "Name", "Keyframe")
                xml.prop("float", "Time", f"{(frame - start) / fps:.6f}")
                xml.close_props()
                roots = [n for n in order if not rest["bones"][n]["p"]]
                write_pose(xml, args.rig, [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
                           [build_tree(r, poses, rest) for r in roots])
                xml.end()
                debug[action_name].append({n: matrix_to_cframe(poses[n]) for n in order})
            xml.end()
            path = OUT_DIR / f"{args.model}_{action_name}.rbxmx"
            path.write_text(xml.text(), encoding="utf-8")
            print(f"[anim] wrote {path.relative_to(REPO)} ({end - start + 1} keyframes, {(end - start) / fps:.2f} s)")
    finally:
        rig.animation_data.action = original_action
    if args.debug_json:
        Path(args.debug_json).write_text(json.dumps(debug))


main()

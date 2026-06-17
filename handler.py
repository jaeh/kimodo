#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
RunPod Serverless Endpoint Handler for Kimodo
Fast Text-to-Motion Generation API

Request format (event['input']):
{
    "prompts": ["A person walks forward"],
    "num_frames": [150],
    "seed": 42,
    "diffusion_steps": 20,
    "cfg_weight": [2.0, 2.0],
    "cfg_type": "scalar",
    "num_samples": 1,
    "constraints": {...},  # optional
    "postprocess_parameters": {},
    "transitions_parameters": {},
    "real_robot_rotations": False
}
"""

import runpod
import os
import sys
import torch
import numpy as np

# Add kimodo to path (in case it's installed via git clone)
sys.path.insert(0, "/workspace/kimodo")
sys.path.insert(0, "/workspace")

from kimodo import load_model
from kimodo.constraints import TYPE_TO_CLASS, Root2DConstraintSet, FullBodyConstraintSet
from kimodo.tools import seed_everything

# Global model instance (loaded once, reused across requests)
_model = None


def get_model():
    """Load and cache the Kimodo model."""
    global _model
    
    if _model is None:
        print("Loading Kimodo model...")
        _model = load_model(
            modelname=os.getenv("KIMODO_MODEL", "Kimodo-SOMA-RP-v1"),
            device="cuda",
            eval_mode=True,
        )
        _model = _model.eval()
        print("Model loaded successfully")
    
    return _model


def _build_constraints(constraints_dict, model):
    """Build model constraints from serialized constraint data."""
    if not constraints_dict:
        return []
    
    model_skeleton = model.skeleton
    model_constraints = []
    
    for constraint_type, data in constraints_dict.items():
        frame_indices = torch.tensor(data["frame_indices"])
        
        if constraint_type == "root2d":
            smooth_root_2d = torch.tensor(data["smooth_root_2d"])
            model_constraints.append(
                Root2DConstraintSet(model_skeleton, frame_indices, smooth_root_2d)
            )
        elif constraint_type == "fullbody":
            joints_pos = torch.tensor(data["joints_pos"])
            joints_rot = torch.tensor(data["joints_rot"])
            smooth_root_2d = torch.tensor(data["smooth_root_2d"]) if data.get("smooth_root_2d") else None
            model_constraints.append(
                FullBodyConstraintSet(
                    model_skeleton, frame_indices, joints_pos, joints_rot, 
                    smooth_root_2d=smooth_root_2d
                )
            )
        else:
            # End effector constraints (may be a list)
            if not isinstance(data, list):
                data = [data]
            for constraint_data in data:
                joint_names = constraint_data.get("joint_names", [])
                joints_pos = torch.tensor(constraint_data["joints_pos"])
                joints_rot = torch.tensor(constraint_data["joints_rot"])
                smooth_root_2d = torch.tensor(constraint_data["smooth_root_2d"]) if constraint_data.get("smooth_root_2d") else None
                
                # Find the constraint class
                for cls_name, cls in TYPE_TO_CLASS.items():
                    if cls_name == constraint_type:
                        model_constraints.append(
                            cls(model_skeleton, frame_indices, joints_pos, joints_rot, 
                                joint_names=joint_names, smooth_root_2d=smooth_root_2d)
                        )
                        break
    
    return model_constraints


def handler(event):
    """
    RunPod serverless handler function.
    
    Accepts GenerationRequest-style input and returns motion data
    compatible with the Kimodo demo's apply_runpod_response.
    """
    try:
        input_data = event.get("input", {})
        
        # Parse request
        prompts = input_data.get("prompts", [])
        num_frames = input_data.get("num_frames", [150])
        seed = input_data.get("seed", 42)
        diffusion_steps = input_data.get("diffusion_steps", 20)
        cfg_weight = input_data.get("cfg_weight", [2.0, 2.0])
        cfg_type = input_data.get("cfg_type", "scalar")
        num_samples = input_data.get("num_samples", 1)
        constraints_dict = input_data.get("constraints")
        postprocess_parameters = input_data.get("postprocess_parameters", {})
        transitions_parameters = input_data.get("transitions_parameters", {})
        real_robot_rotations = input_data.get("real_robot_rotations", False)
        
        if not prompts:
            return {"error": "Missing required field: prompts"}
        
        # Set seed
        seed_everything(seed)
        
        # Load model
        model = get_model()
        
        # Build constraints
        model_constraints = _build_constraints(constraints_dict, model)
        
        # Generate motion
        print(f"Generating motion for prompts: {prompts}")
        
        with torch.no_grad():
            output = model(
                prompts,
                num_frames,
                diffusion_steps,
                multi_prompt=True,
                constraint_lst=model_constraints,
                cfg_weight=cfg_weight,
                num_samples=num_samples,
                cfg_type=cfg_type,
                **(postprocess_parameters | transitions_parameters),
            )
        
        # Extract results
        posed_joints = output["posed_joints"].cpu().numpy()
        global_rot_mats = output["global_rot_mats"].cpu().numpy()
        foot_contacts = output.get("foot_contacts")
        if foot_contacts is not None:
            foot_contacts = foot_contacts.cpu().numpy()
        
        # Return as JSON-serializable dict
        return {
            "posed_joints": posed_joints.tolist(),
            "global_rot_mats": global_rot_mats.tolist(),
            "foot_contacts": foot_contacts.tolist() if foot_contacts is not None else None,
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})

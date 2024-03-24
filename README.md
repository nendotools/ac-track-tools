<div align="center" style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
  <h1>Assetto Corsa Track Tools</h1>
  <div>BLENDER 3D add-on</div>
  <div><sup>Track Configuration Manager</sup></div>
  <div style="display: flex; flex-direction: row;">
    <img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/nendotools/ac-track-tools?style=flat-square">
    <img alt="GitHub Workflow Status (with branch)" src="https://img.shields.io/github/actions/workflow/status/nendotools/ac-track-tools/linting.yml?style=flat-square">
    <img alt="GitHub issues" src="https://img.shields.io/github/issues-raw/nendotools/ac-track-tools?style=flat-square">
    <img alt="GitHub" src="https://img.shields.io/github/license/nendotools/ac-track-tools?style=flat-square">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/fake-bpy-module-latest?style=flat-square">
  </div>
</div>

### Table of Contents

- [Overview](#overview)
- [TODO](#todo)

### Overview

Assetto Corsa Track Tools is a Blender 3D add-on built to streamline the process of creating and configuring tracks by
exposing various configuration options in a more digestible and intuitive manner. It provides several quality of life
tools to help manage track settings, surfaces, track/race nodes, cameras, lighting, sounds, and more.

This project is still in its early stages, and many features are still in development. If you have any suggestions or
requests, please feel free to open an issue or pull request.

### TODO

- [x] Track Settings
  - [x] Name + Description
  - [x] Tags
  - [x] Metadata
  - [x] save/load
- [x] Surfaces + Nodes
  - [x] Assign Surface, Wall, Physics
  - [x] Create Race Nodes
    - [x] Start
    - [x] Finish
    - [x] A-B Start + Finish
    - [x] Hotlap Start
    - [x] Time Gate
    - [x] Pit
- [ ] Cameras
  - [ ] Attach Camera
  - [ ] Focus Movement
  - [ ] Monitor Groups
- [x] Lighting
  - [x] Sun
  - Extension (WIP)
    - [x] Spotlights
    - [ ] Mesh Lights
    - [ ] Line Lights
    - [ ] Light Series
- [ ] Map
  - [ ] Generate Map
    - over head view of track
    - disable all non-track objects
    - black and white
    - resolution config
    - save mini version as ui/outline.png (for track selection)
    - save full version as map.png (for mini-map and loading screen)
- [ ] Overlays: Time-Attack
- [ ] Sections: Track Regions
- [ ] Groove
  - Investigate Implementation
- [ ] AI
  - Investigate Implementation
- [x] Sounds
  - [x] Reverb Zones
  - [x] Sound Sources
- [ ] Animation
  - Investigate Implementation
- [ ] Multi-Modal Configuration
  - Investigate Implementation
  - useful to reuse track without reconfiguring everything
- [ ] Export
  - [x] Track
  - [x] Surface
  - [ ] Models
  - [ ] Cameras
  - [ ] Lighting
  - [x] Sounds

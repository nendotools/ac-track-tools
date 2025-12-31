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

> [!WARNING]
> I've taken a hiatus from maintaining this project to focus on some other things. FuzzysAltTabGarage has picked it up to continue development.

### Table of Contents

- [Overview](#overview)
- [Features](#features)
- [TODO](#todo)

### Overview

Assetto Corsa Track Tools is a Blender 3D add-on built to streamline the process of creating and configuring tracks by
exposing various configuration options in a more digestible and intuitive manner. It provides several quality of life
tools to help manage track settings, surfaces, track/race nodes, cameras, lighting, sounds, and more.

This project is still in its early stages, and many features are still in development. If you have any suggestions or
requests, please feel free to open an issue or pull request.

#### Objectives

- Simplify the process of creating and configuring tracks for Assetto Corsa
- Provide a more intuitive and user-friendly interface for managing track settings
- Automate common tasks and checks to reduce human error
- Provide clear and explicit defaults and ranges for all settings to reduce ambiguity

### Features

#### Configuration Management

Save/Load track settings, surfaces, nodes, cameras, lighting, and sound settings. This allows for not only effortless
validation of inputs, but also binds all track configurations to the Blender project file.

Project initialization automatically creates the necessary folder structure and files to configure the track once the
working directory is set.

Pre-flight checks are also performed to ensure that all required settings are present before exporting the track. It's
also able to correct some common issues automatically.

#### Surfaces

Default surfaces are automatically available. Surfaces can easily be added, modified, and overridden from the UI.
Surfaces can be easily assigned to selected meshes from the context menu (right click). The UI also allows for easily
selecting all meshes with an assigned surface.

#### Track Nodes

Race start locations, time gates, and pitboxes can be added from the context menu and moved around the track where
needed. The preflight check ensures that start locations and pitboxes are even and the ui_track.json file is updated.

#### Lighting

Currently, the sun settings and some basic lighting extension options are available from the UI. In the future, more
advanced settings and mesh bindings will be added to simplify the process of adding the various lighting options
available through modding.

#### Sounds

Reverb zones and sound emitters can be added from the context menu. Some default example reverb options are available
and can be easily customized to fit the track's needs. Sounds require some additional work outside of Blender to be
usable in Assetto Corsa, but the add-on provides the necessary settings to hook them up once banks are created.

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
- [x] Map
  - [x] Generate Map
    - overhead view of track
    - disable all non-track objects
    - black and white
    - resolution config
    - save mini version as ui/outline.png (for track selection)
    - save full version as map.png (for mini-map and loading screen)
  - [x] Generate Preview (ui/preview.png)
- [x] Track Layouts/Variants
  - [x] Multiple layout support (club, national, etc.)
  - [x] Collection-to-KN5 mapping
  - [x] Per-layout models.ini generation
  - [x] Preview mode for layout visualization
  - [x] Default layout protection
- [ ] Object Setup
  - [x] Auto-setup for trees
  - [x] Auto-setup for grass
  - [x] Auto-setup for standard objects
  - [x] Batch object configuration
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
  - [x] Track (FBX)
  - [x] Surface
  - [x] Models (models.ini per layout)
  - [x] KN5 (experimental)
    - [ ] Testing and verification
  - [ ] Cameras
  - [ ] Lighting
  - [x] Sounds

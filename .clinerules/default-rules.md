# .clinerules for YoloClanker

## Project Context
YoloClanker is a dedicated testing ground for Yolo mode and other experimental Cline features. This folder is isolated for bold experimentation without impacting other projects.

## Available Projects
- **YoloClanker**: Experimental Cline feature testing (current)
- **HelloKnight** (Godot_Projects/HelloKnight): 2D action RPG/Souls-like game
- **SFXClanker** (VSCode Projects/SFXClanker): Python GUI for SFX generation
- **GoblinAnimationCompleter and Sprite Analyzer** (VSCode Projects/): Sprite tools

## Navigation Rules
- Use @workspace:path for cross-project references (e.g., @HelloKnight:scripts/player.gd)
- Configure workspaces in Cline settings for shortcuts
- This project loads this .clinerules automatically

## Yolo Mode Guidelines
- Enable Yolo mode for high-risk, high-reward suggestions
- Test experimental features here first
- Document outcomes in CLINE.md for lessons learned
- Prioritize innovation over safety in this folder

## Best Practices
- Specify project context in queries
- Use relative paths within YoloClanker
- No git repo yet (experimental)
- Test Cline features thoroughly before applying elsewhere

## File Organization
- Keep experimental code/docs in YoloClanker/
- Use ASSET DUMP for shared resources if needed
- Fails/ for failed experiments (reference only)

## Version Control
- No git yet; experimental phase
- Future: separate repo if stable

## Dev Workflow Rules
- Plan: Update .clinerules with test plans
- Test: Use Yolo mode in this folder
- Document: Add lessons here
- Iterate: Refine based on findings

## Status v0.1
- Docs setup complete, experimental phase

## Dev Workflow Rules
- Plan: Update yoloClanker.design.md with test plans
- Test: Use Yolo mode in this folder
- Document: Add lessons here
- Iterate: Refine based on findings

## Future Expansion
- Yolo mode risk assessment
- New Cline capabilities validation

Last updated: 2026-03-27

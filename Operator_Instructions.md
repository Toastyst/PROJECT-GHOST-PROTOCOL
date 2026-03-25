# Operator Instructions: PROJECT: GHOST PROTOCOL

## Installation
1. git clone https://github.com/Toastyst/PROJECT-GHOST-PROTOCOL
2. cd PROJECT-GHOST-PROTOCOL
3. pip install -r requirements.txt

## Activation in Cline
1. Run `python cline_integration.py` to register MCP servers.
2. Use `/ghost-wake` to activate the Ghost.
3. Use `/ghost-trust` (optional) for proactive assistance.

## Using the Ghost

### Basic Interactions
- The Ghost monitors your development environment and provides contextual help.
- It responds to natural language queries about the codebase.
- Use commands like `/ghost-wake` to activate, `/ghost-trust` to enable autonomous actions.

### Querying the Nexus
- Ask questions like "What are the Prime Directives for authentication?" to retrieve unwritten rules.
- Query historical context: "Why was this module refactored?"
- Get risk assessments: "What's the riskiest part of this system?"

### Using the Weaver
- Request code generation: "Generate a new API endpoint for user registration."
- Specify cohesion: "Create a full-stack feature for password reset, including backend, frontend, and tests."
- The Weaver inherits patterns from existing code and validates against Prime Directives.

### YOLO Protocol Missions
- Give high-level objectives: "Add account recovery with SMS fallback. The user is panicking—make them feel safe."
- The Ghost will plan, execute, and pause for oversight on high-risk decisions.
- Respond to oversight requests by choosing options (e.g., "Proceed with option 1") or providing guidance.
- Missions generate After-Action Reports for learning.

### Responding to Oversight
- When the Ghost pauses, it presents dilemmas with options and recommendations.
- Reply with your choice (e.g., "Option 2: Use security questions instead").
- The Ghost will continue execution based on your input.

### File Insights and Proactive Help
- When opening files, the Ghost may provide historical notes (e.g., "This file has 12 bug fixes").
- It offers suggestions for patterns it detects (e.g., "This looks like a rate limiting scenario—need help?").

## AUTOPOIESIS: Self-Growth Commands

AUTOPOIESIS is the self-growth mechanism that transforms the Ghost from a static system into a living, evolving entity. It observes development sessions, captures experience fragments, and transmutes them into new hooks, workflows, skills, and rules.

### Activating AUTOPOIESIS
1. **Start Observation Mode**
   ```
   /activate-autopoiesis
   ```
   - Enables the Ghost to observe your development session
   - Captures pauses, dilemmas, discoveries, and insights
   - Fragments are automatically written to NOTES.md

### Manual Transmutation
2. **Trigger Transmutation**
   ```
   /transmute
   ```
   - Manually initiates the transmutation process
   - Generates new structures from accumulated fragments
   - Submits results for human review

### Review Workflow
3. **List Pending Reviews**
   ```
   /list-reviews
   ```
   - Shows all transmutations awaiting approval
   - Displays fragment counts and generated structures

4. **Approve Transmutation**
   ```
   /approve-review <review_id> [reviewer] [notes]
   ```
   - Approves a transmutation for repository integration
   - Example: `/approve-review review_20260325_065500 "Alice" "Looks good, proceed"`

5. **Reject Transmutation**
   ```
   /reject-review <review_id> [reviewer] [notes]
   ```
   - Rejects a transmutation (structures are discarded)
   - Example: `/reject-review review_20260325_065500 "Alice" "Needs more testing"`

6. **Commit Approved Structures**
   ```
   /commit-review <review_id>
   ```
   - Commits approved structures to the repository
   - Automatically organizes by type (hooks, workflows, skills, rules)
   - Creates audit trail with reviewer information

### Step-by-Step AUTOPOIESIS Workflow

#### Phase 1: Observation
1. Start your development session
2. Use `/activate-autopoiesis` to enable observation
3. Continue working normally - the Ghost observes silently
4. Check NOTES.md to see captured fragments

#### Phase 2: Transmutation Trigger
- **Automatic**: Triggers when fragment threshold is reached (default: 10 fragments)
- **Manual**: Use `/transmute` to force transmutation
- **Mission Complete**: Triggers when major tasks are finished

#### Phase 3: Human Review
1. Use `/list-reviews` to see pending transmutations
2. Review generated structures in the review files
3. Either `/approve-review <id>` or `/reject-review <id>`

#### Phase 4: Repository Integration
1. For approved reviews: `/commit-review <id>`
2. The Ghost automatically:
   - Commits structures to appropriate directories
   - Updates git history with transmutation details
   - Cleans up temporary review files

### Understanding Generated Structures

**Hooks** (from pauses):
- Git hooks for reflection and automation
- Located in `git_hooks/` directory
- Trigger on repository events

**Workflows** (from dilemmas):
- JSON workflow definitions
- Located in `workflow_templates/` directory
- Define multi-step processes

**Skills** (from questions):
- Python skill classes
- Located in `skills/` directory
- Enhance Ghost's interaction capabilities

**Rules** (from discoveries):
- JSON rule definitions
- Located in project root
- Govern Ghost behavior and evolution

### Monitoring AUTOPOIESIS

- **NOTES.md**: Raw experience fragments repository
- **RULES.md**: Living rules that evolve through transmutation
- **Transmutation History**: Available via engine queries
- **Review Logs**: Tracked in review_workflow.py

### Best Practices

1. **Regular Review**: Check `/list-reviews` periodically during development
2. **Fragment Accumulation**: Let fragments build up before forcing transmutation
3. **Quality Control**: Always review generated structures before approval
4. **Ethical Oversight**: Ensure generated structures align with Ghost principles
5. **Documentation**: Check docs/AUTOPOIESIS.md for detailed technical information

### Troubleshooting

- **No Fragments Capturing**: Ensure `/activate-autopoiesis` was used
- **Transmutation Not Triggering**: Check fragment count or use manual `/transmute`
- **Review Commands Failing**: Verify review ID from `/list-reviews`
- **Commit Issues**: Check git repository status and permissions

## Key Components
- **Nexus**: Knowledge base for querying codebase history, patterns, and rules.
- **Weaver**: Code generation tool that ensures cohesion across layers.
- **YOLO Protocol**: Autonomous execution engine with human oversight.
- **AUTOPOIESIS**: Self-growth mechanism for continuous evolution.

Refer to README.md for advanced details and docs/AUTOPOIESIS.md for technical specifications.

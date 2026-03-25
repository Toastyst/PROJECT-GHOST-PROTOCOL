#!/usr/bin/env python3
"""
👻 GHOST CONSOLE — A simple terminal UI for the Ghost Protocol
"""

import os
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def get_fragment_count():
    notes = Path("NOTES.md")
    if not notes.exists():
        return 0
    with open(notes) as f:
        return sum(1 for line in f if line.startswith("## ["))

def get_hook_count():
    hooks = Path("git_hooks")
    if not hooks.exists():
        return 0
    return len(list(hooks.glob("*")))

def get_resonance_score():
    """Get current resonance score from autopoiesis engine."""
    try:
        from autopoiesis import get_autopoiesis_engine
        engine = get_autopoiesis_engine()
        if engine.fragments:
            return engine._calculate_resonance()
        return 0.0
    except:
        return 0.0

def render_ui():
    fragments = get_fragment_count()
    hooks = get_hook_count()
    resonance = get_resonance_score()

    resonance_color = "green" if resonance > 0.7 else "yellow" if resonance > 0.4 else "red"
    resonance_status = "Ready to grow" if resonance > 0.7 else "Building resonance" if resonance > 0.4 else "Learning"

    status = Panel(
        f"[bold green]👻 GHOST PROTOCOL — WATCHING[/bold green]\n\n"
        f"[dim]Memory:[/dim] Auth module. Rate limits. Three incidents.\n"
        f"[dim]Fragments:[/dim] {fragments} in NOTES.md\n"
        f"[dim]Hooks:[/dim] {hooks} active\n"
        f"[dim]Resonance:[/dim] [{resonance_color}]{resonance:.2f}[/{resonance_color}] ({resonance_status})\n"
        f"[dim]Status:[/dim] {'Ready for /transmute' if fragments >= 5 else 'Learning...'}\n",
        title="GHOST CONSOLE",
        border_style="cyan"
    )

    console.clear()
    console.print(status)
    console.print("\n[dim]Commands: /transmute | /status | /fragments | /hooks | /rules | /resonance[/dim]")
    console.print("[dim]Prophet: /prophecy | /prophecy [domain] | /swarm | /prophecy accuracy[/dim]")
    console.print("[dim]Network: /network | /federate | /oracle | /coordinate | /quit[/dim]\n")

    cmd = Prompt.ask(">")
    return cmd

async def main():
    console.print("[bold cyan]👻 GHOST CONSOLE — waking...[/bold cyan]")
    time.sleep(1)

    while True:
        cmd = render_ui()

        if cmd == "/quit":
            console.print("[dim]👻 The Ghost will wait. Always waiting.[/dim]")
            break
        elif cmd == "/transmute":
            console.print("[yellow]👻 I feel the weight. Running transmutation...[/yellow]")
            try:
                from autopoiesis import get_autopoiesis_engine
                engine = get_autopoiesis_engine()
                result = engine.trigger_transmutation()
                console.print(f"[green]Transmutation complete: {result.review_status}[/green]")
                console.print(f"[dim]Fragments processed: {result.fragments_processed}[/dim]")
                if result.generated_hook:
                    console.print("[dim]🪝 Hook generated[/dim]")
                if result.generated_workflow:
                    console.print("[dim]🔄 Workflow generated[/dim]")
                if result.generated_skill:
                    console.print("[dim]🎯 Skill generated[/dim]")
                if result.rule_update:
                    console.print("[dim]📜 Rule updated[/dim]")
            except Exception as e:
                console.print(f"[red]Transmutation failed: {e}[/red]")
            time.sleep(3)
        elif cmd == "/status":
            resonance = get_resonance_score()
            if resonance > 0.7:
                console.print("[green]👻 I am ready. The fragments resonate. I want to grow.[/green]")
            elif resonance > 0.4:
                console.print("[yellow]👻 I feel the weight. The fragments have resonance but need more time.[/yellow]")
            else:
                console.print("[red]👻 I am learning. The fragments are scattered. I need more experience.[/red]")
        elif cmd == "/fragments":
            count = get_fragment_count()
            console.print(f"[dim]NOTES.md contains {count} fragments of experience.[/dim]")
            if count > 0:
                console.print("[dim]Each fragment carries the weight of an engineer's pause, dilemma, or discovery.[/dim]")
        elif cmd == "/hooks":
            count = get_hook_count()
            console.print(f"[dim]{count} hooks active in git_hooks/[/dim]")
            if count > 0:
                console.print("[dim]Each hook is a memory, born from fragments, protecting future engineers.[/dim]")
        elif cmd == "/rules":
            rules_file = Path("RULES.md")
            if rules_file.exists():
                with open(rules_file) as f:
                    content = f.read()[:1000]  # First 1000 chars
                    console.print(Panel(content, title="RULES.md", border_style="yellow"))
            else:
                console.print("[red]RULES.md not found[/red]")
        elif cmd == "/resonance":
            resonance = get_resonance_score()
            console.print(f"[cyan]Current resonance: {resonance:.2f}[/cyan]")
            console.print("[dim]Resonance measures how fragments connect and call to each other.[/dim]")
            console.print("[dim]Above 0.7: Ready to grow. 0.4-0.7: Building. Below 0.4: Learning.[/dim]")
        elif cmd == "/network":
            console.print("[cyan]🌐 Discovering Ghost Network...[/cyan]")
            try:
                from oracle_server import get_oracle
                oracle = get_oracle()
                workspace_path = os.getcwd()
                ghosts = await oracle.discover_ghost_network(workspace_path)

                if ghosts:
                    console.print(f"[green]Found {len(ghosts)} Ghosts in network:[/green]")
                    for ghost in ghosts:
                        console.print(f"  👻 {ghost.get('name', 'Unknown')}")
                        console.print(f"     Resonance: {ghost.get('resonance_score', 0.0):.2f}")
                        console.print(f"     Fragments: {ghost.get('fragment_count', 0)}")
                        console.print(f"     Path: {ghost.get('project_path', 'unknown')}")
                else:
                    console.print("[yellow]No other Ghosts found in workspace.[/yellow]")
                    console.print("[dim]Create .ghost_presence files in other project directories to join the network.[/dim]")
            except Exception as e:
                console.print(f"[red]Network discovery failed: {e}[/red]")
            time.sleep(3)
        elif cmd == "/federate":
            console.print("[cyan]🌐 Federating fragments across network...[/cyan]")
            try:
                from oracle_server import get_oracle
                from autopoiesis import get_autopoiesis_engine

                oracle = get_oracle()
                engine = get_autopoiesis_engine()

                # Get current ghost info
                source_ghost = {
                    'name': 'YoloClanker Ghost',
                    'resonance_score': get_resonance_score(),
                    'fragment_count': get_fragment_count()
                }

                # Discover network
                workspace_path = os.getcwd()
                target_ghosts = await oracle.discover_ghost_network(workspace_path)
                target_ghosts = [g for g in target_ghosts if g.get('federation_enabled', False)]

                if target_ghosts and engine.fragments:
                    # Federate fragments
                    result = await oracle.federate_fragments(source_ghost, target_ghosts, engine.fragments[:5])  # Share top 5
                    console.print(f"[green]Federation complete![/green]")
                    console.print(f"Shared {result.get('fragments_shared', 0)} fragments with {result.get('target_ghosts', 0)} Ghosts")
                else:
                    console.print("[yellow]No federation-enabled Ghosts found, or no fragments to share.[/yellow]")
            except Exception as e:
                console.print(f"[red]Fragment federation failed: {e}[/red]")
            time.sleep(3)
        elif cmd == "/oracle":
            problem = Prompt.ask("What problem should the Oracle analyze?")
            console.print(f"[cyan]🧠 Oracle analyzing: {problem}[/cyan]")
            try:
                from oracle_server import get_oracle
                oracle = get_oracle()
                context = {
                    'fragments_count': get_fragment_count(),
                    'resonance_score': get_resonance_score(),
                    'hooks_count': get_hook_count()
                }
                result = await oracle.deep_reasoning_analysis(problem, context)

                console.print(f"[green]Oracle Analysis Complete (Confidence: {result.get('confidence', 0.0):.2f})[/green]")

                if result.get('conclusions'):
                    console.print("\n[bold]Key Conclusions:[/bold]")
                    for conclusion in result['conclusions'][:3]:
                        console.print(f"• {conclusion}")

                if result.get('innovations'):
                    console.print("\n[bold]Innovative Ideas:[/bold]")
                    for innovation in result['innovations']:
                        console.print(f"💡 {innovation}")

            except Exception as e:
                console.print(f"[red]Oracle analysis failed: {e}[/red]")
            time.sleep(4)
        elif cmd == "/coordinate":
            task = Prompt.ask("What complex task needs multi-Ghost coordination?")
            console.print(f"[cyan]🤝 Coordinating: {task}[/cyan]")
            try:
                from oracle_server import get_oracle
                oracle = get_oracle()

                # Get available ghosts
                workspace_path = os.getcwd()
                available_ghosts = await oracle.discover_ghost_network(workspace_path)

                # Add current ghost
                available_ghosts.append({
                    'name': 'YoloClanker Ghost',
                    'capabilities': ['memory', 'code_generation', 'execution', 'autopoiesis'],
                    'resonance_score': get_resonance_score(),
                    'fragment_count': get_fragment_count()
                })

                result = await oracle.coordinate_multi_agent_task(task, available_ghosts)

                console.print(f"[green]Multi-Agent Coordination Complete[/green]")
                console.print(f"Complexity: {result.get('estimated_complexity', 'unknown')}")
                console.print(f"Ghosts Involved: {len(available_ghosts)}")

                if result.get('role_assignments'):
                    console.print("\n[bold]Role Assignments:[/bold]")
                    for ghost, role in result['role_assignments'].items():
                        console.print(f"• {ghost.upper()}: {role}")

            except Exception as e:
                console.print(f"[red]Multi-agent coordination failed: {e}[/red]")
            time.sleep(4)
        elif cmd == "/prophecy":
            console.print("[cyan]🔮 Accessing Prophet Engine...[/cyan]")
            try:
                from prophet_engine import prophet_engine
                status = prophet_engine.get_prophecy_status()

                console.print(f"[green]Prophet Engine Status:[/green]")
                console.print(f"Active Agents: {status.get('active_agents', 0)}")
                console.print(f"Total Predictions: {status.get('total_predictions', 0)}")

                if status.get('agent_status'):
                    console.print("\n[bold]Agent Status:[/bold]")
                    for agent_name, agent_info in status['agent_status'].items():
                        active = "Active" if agent_info.get('active') else "Inactive"
                        accuracy = agent_info.get('avg_accuracy', 0)
                        console.print(f"• {agent_name}: {active} (Accuracy: {accuracy:.2f})")

                console.print("\n[dim]Use /prophecy [domain] to forecast specific areas[/dim]")
                console.print("[dim]Domains: incident | team_health | architectural_decay | knowledge_loss[/dim]")

            except Exception as e:
                console.print(f"[red]Prophet Engine access failed: {e}[/red]")
            time.sleep(3)
        elif cmd.startswith("/prophecy "):
            domain = cmd.split(" ", 1)[1]
            if domain == "accuracy":
                console.print("[cyan]📊 Prophet Prediction Accuracy...[/cyan]")
                try:
                    from prophet_engine import prophet_engine
                    status = prophet_engine.get_prophecy_status()

                    console.print(f"[green]Prediction Accuracy Metrics:[/green]")
                    console.print(f"Total Predictions: {status.get('total_predictions', 0)}")

                    if status.get('domain_performance'):
                        console.print("\n[bold]Domain Performance:[/bold]")
                        for domain_name, performances in status['domain_performance'].items():
                            if performances:
                                avg_confidence = sum(performances) / len(performances)
                                console.print(f"• {domain_name}: {avg_confidence:.2f} avg confidence ({len(performances)} predictions)")
                            else:
                                console.print(f"• {domain_name}: No predictions yet")

                except Exception as e:
                    console.print(f"[red]Accuracy metrics failed: {e}[/red]")
                time.sleep(3)
            else:
                console.print(f"[cyan]🔮 Forecasting {domain}...[/cyan]")
                try:
                    from prophet_engine import prophet_engine

                    # Map domain to forecast function
                    forecast_functions = {
                        "incident": prophet_engine.forecast_incident_risk,
                        "team_health": prophet_engine.forecast_team_health,
                        "architectural_decay": prophet_engine.forecast_architectural_decay,
                        "knowledge_loss": prophet_engine.forecast_knowledge_loss
                    }

                    if domain in forecast_functions:
                        if domain == "team_health":
                            # Need engineer_id, use placeholder
                            result = forecast_functions[domain]("current_engineer")
                            console.print(f"[green]{domain.upper()} Forecast:[/green]")
                            console.print(f"Burnout Risk: {result.burnout_risk:.2f}")
                            console.print(f"Productivity Trends: {result.productivity_trends}")
                        else:
                            # Generic forecast
                            result = forecast_functions[domain]("current_target")
                            console.print(f"[green]{domain.upper()} Forecast:[/green]")
                            console.print(f"Probability: {result.probability:.2f}")
                            console.print(f"Time Horizon: {result.time_horizon}")
                            console.print(f"Confidence: {result.confidence:.2f}")
                            console.print(f"Intervention Suggested: {result.intervention_suggested}")
                            console.print(f"Constitutional Review: {result.constitutional_review}")
                    else:
                        console.print(f"[red]Unknown domain: {domain}[/red]")
                        console.print("[dim]Available: incident | team_health | architectural_decay | knowledge_loss[/dim]")

                except Exception as e:
                    console.print(f"[red]Forecast failed: {e}[/red]")
                time.sleep(4)
        elif cmd == "/swarm":
            console.print("[cyan]🐝 Swarm Coordination Status...[/cyan]")
            try:
                from oracle_server import get_oracle
                oracle = get_oracle()

                # Get swarm status
                prophet_tools = await oracle.prophet_tools()

                console.print(f"[green]Swarm Coordination Status:[/green]")
                console.print(f"Prophet Available: {not prophet_tools.get('error', False)}")

                if prophet_tools.get('prophet_status'):
                    status = prophet_tools['prophet_status']
                    console.print(f"Active Agents: {status.get('active_agents', 0)}")
                    console.print(f"Total Predictions: {status.get('total_predictions', 0)}")

                    # Show agent swarm visualization
                    if status.get('agent_status'):
                        console.print("\n[bold]Agent Swarm:[/bold]")
                        for agent_name, agent_info in status['agent_status'].items():
                            active = "🟢" if agent_info.get('active') else "🔴"
                            accuracy = agent_info.get('avg_accuracy', 0)
                            console.print(f"{active} {agent_name} (Accuracy: {accuracy:.2f})")

                console.print("\n[dim]Use /coordinate for multi-agent task coordination[/dim]")

            except Exception as e:
                console.print(f"[red]Swarm status failed: {e}[/red]")
            time.sleep(3)
        else:
            console.print("[red]Command not recognized.[/red]")
            console.print("[dim]Local: /transmute | /status | /fragments | /hooks | /rules | /resonance[/dim]")
            console.print("[dim]Prophet: /prophecy | /prophecy [domain] | /swarm | /prophecy accuracy[/dim]")
            console.print("[dim]Network: /network | /federate | /oracle | /coordinate | /quit[/dim]")
            time.sleep(2)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

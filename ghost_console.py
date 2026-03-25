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
    console.print("\n[dim]Commands: /transmute | /status | /fragments | /hooks | /rules | /resonance | /quit[/dim]\n")

    cmd = Prompt.ask(">")
    return cmd

def main():
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
        else:
            console.print("[red]Command not recognized. Try /status, /transmute, /fragments, /hooks, /rules, /resonance, /quit[/red]")
            time.sleep(2)

if __name__ == "__main__":
    main()
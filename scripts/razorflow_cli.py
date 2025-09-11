#!/usr/bin/env python3
"""
Razorflow-AI CLI Management Tool
Command-line interface for managing AI assistant deployments
"""

import asyncio
import click
import sys
from pathlib import Path

# Add API directory to path
sys.path.append(str(Path(__file__).parent.parent / "api"))

from scripts.razorflow_setup import RazorflowSetup


@click.group()
def cli():
    """Razorflow-AI Management CLI"""
    pass


@cli.command()
def setup():
    """Initialize the Razorflow-AI system"""
    click.echo("🚀 Initializing Razorflow-AI System...")

    async def run_setup():
        setup_manager = RazorflowSetup()
        results = await setup_manager.initialize_razorflow_system()
        setup_manager.print_setup_summary(results)

    asyncio.run(run_setup())


@cli.command()
@click.option("--name", default="Demo Client", help="Name for demo client")
def demo(name):
    """Create a demo client deployment"""
    click.echo(f"🎯 Creating demo deployment for: {name}")

    async def run_demo():
        setup_manager = RazorflowSetup()
        result = await setup_manager.create_demo_client_deployment(name)
        click.echo(f"Demo Result: {result}")

    asyncio.run(run_demo())


@cli.command()
def templates():
    """List available assistant templates"""
    click.echo("📋 Available Assistant Templates:")

    async def list_templates():
        from services.template_manager import TemplateManager

        template_manager = TemplateManager()

        templates = await template_manager.list_available_templates()

        for template in templates:
            click.echo(f"  • {template['name']} ({template['template_id']})")
            click.echo(f"    Category: {template['category']}")
            click.echo(f"    Price: ${template.get('base_price', 'N/A')}")
            click.echo()

    asyncio.run(list_templates())


@cli.command()
@click.argument("client_id", type=int)
@click.argument("template_type")
@click.option("--priority", default="normal", help="Build priority")
def deploy(client_id, template_type, priority):
    """Deploy assistant for specific client"""
    click.echo(f"🚀 Deploying {template_type} for client {client_id}")

    async def run_deploy():
        from services.razorflow_integration import RazorflowIntegration

        razorflow = RazorflowIntegration()

        result = await razorflow.queue_client_build(
            client_id=client_id, template_type=template_type, priority=priority
        )
        click.echo(f"Deployment queued: {result}")

    asyncio.run(run_deploy())


@cli.command()
@click.argument("build_id")
def status(build_id):
    """Check build status"""
    click.echo(f"🔍 Checking status for build: {build_id}")

    async def check_status():
        from services.razorflow_integration import RazorflowIntegration

        razorflow = RazorflowIntegration()

        result = await razorflow.get_build_status(build_id)
        click.echo(f"Build Status: {result}")

    asyncio.run(check_status())


@cli.command()
def health():
    """Run system health check"""
    click.echo("🔍 Running Razorflow-AI Health Check...")

    async def run_health():
        setup_manager = RazorflowSetup()
        health_status = await setup_manager._run_system_health_check()

        click.echo("\nHealth Check Results:")
        for component, status in health_status.items():
            status_icon = "✅" if status else "❌"
            click.echo(f"  {status_icon} {component}: {status}")

    asyncio.run(run_health())


if __name__ == "__main__":
    cli()

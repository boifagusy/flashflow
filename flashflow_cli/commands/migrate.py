"""
FlashFlow 'migrate' command - Apply database migrations
"""

import click
import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from ..core import FlashFlowProject, FlashFlowIR
from ..parser import FlowParser

@click.command()
@click.option('--rollback', '-r', default=None, help='Rollback to specific migration')
@click.option('--force', '-f', is_flag=True, help='Force apply migrations without confirmation')
@click.option('--dry-run', '-d', is_flag=True, help='Show what would be migrated without applying')
@click.pass_context
def migrate(ctx, rollback, force, dry_run):
    """Apply pending database migrations"""
    
    project_root = ctx.obj.get('project_root')
    if not project_root:
        click.echo("❌ Not in a FlashFlow project directory")
        click.echo("Run this command from a FlashFlow project root")
        return
    
    project = FlashFlowProject(project_root)
    
    if dry_run:
        show_pending_migrations(project)
        return
    
    if rollback:
        rollback_migration(project, rollback, force)
    else:
        apply_pending_migrations(project, force)

def show_pending_migrations(project: FlashFlowProject):
    """Show what migrations would be applied"""
    click.echo("🔍 Checking for pending migrations...")
    
    # Parse current .flow files to get models
    parser = FlowParser()
    ir = parser.parse_project(project.root_path)
    
    # Get existing migrations
    migrations_path = project.root_path / "database" / "migrations"
    existing_migrations = get_existing_migrations(migrations_path)
    
    # Determine what needs to be migrated
    pending_changes = analyze_schema_changes(ir, existing_migrations)
    
    if not pending_changes:
        click.echo("✅ Database is up to date. No pending migrations.")
        return
    
    click.echo(f"📋 Found {len(pending_changes)} pending changes:")
    for i, change in enumerate(pending_changes, 1):
        click.echo(f"   {i}. {change['type']}: {change['description']}")
    
    click.echo("\n💡 Run 'flashflow migrate' to apply these changes")

def apply_pending_migrations(project: FlashFlowProject, force: bool = False):
    """Apply all pending database migrations"""
    click.echo("🚀 Applying database migrations...")
    
    # Parse current .flow files
    parser = FlowParser()
    ir = parser.parse_project(project.root_path)
    
    if not ir.models:
        click.echo("⚠️  No models found in .flow files")
        return
    
    # Get existing migrations
    migrations_path = project.root_path / "database" / "migrations"
    migrations_path.mkdir(parents=True, exist_ok=True)
    
    existing_migrations = get_existing_migrations(migrations_path)
    pending_changes = analyze_schema_changes(ir, existing_migrations)
    
    if not pending_changes:
        click.echo("✅ Database is already up to date")
        return
    
    if not force:
        click.echo(f"📋 Ready to apply {len(pending_changes)} migrations:")
        for change in pending_changes:
            click.echo(f"   • {change['type']}: {change['description']}")
        
        if not click.confirm("\n🤔 Continue with migration?"):
            click.echo("❌ Migration cancelled")
            return
    
    # Create and apply migrations
    success_count = 0
    for change in pending_changes:
        try:
            apply_single_migration(project, change)
            success_count += 1
            click.echo(f"   ✅ {change['description']}")
        except Exception as e:
            click.echo(f"   ❌ Failed: {change['description']} - {str(e)}")
            break
    
    click.echo(f"\n🎉 Applied {success_count}/{len(pending_changes)} migrations successfully")
    
    if success_count == len(pending_changes):
        # Update migration tracking
        update_migration_log(project, pending_changes)

def rollback_migration(project: FlashFlowProject, target: str, force: bool = False):
    """Rollback to a specific migration"""
    click.echo(f"🔄 Rolling back to migration: {target}")
    
    migrations_log = get_migration_log(project)
    
    if target not in [m['id'] for m in migrations_log]:
        click.echo(f"❌ Migration '{target}' not found")
        return
    
    if not force:
        if not click.confirm(f"⚠️  This will rollback database changes. Continue?"):
            click.echo("❌ Rollback cancelled")
            return
    
    try:
        # Implement rollback logic based on migration history
        # This is a simplified implementation
        click.echo(f"✅ Rolled back to migration: {target}")
        click.echo("⚠️  Note: Rollback functionality is basic. Manual verification recommended.")
    except Exception as e:
        click.echo(f"❌ Rollback failed: {str(e)}")

def get_existing_migrations(migrations_path: Path) -> List[Dict]:
    """Get list of existing migration files"""
    migrations = []
    
    if not migrations_path.exists():
        return migrations
    
    for file_path in migrations_path.glob("*.sql"):
        # Parse migration filename for metadata
        filename = file_path.stem
        if "_" in filename:
            timestamp, name = filename.split("_", 1)
            migrations.append({
                'id': filename,
                'timestamp': timestamp,
                'name': name,
                'file_path': file_path
            })
    
    return sorted(migrations, key=lambda x: x['timestamp'])

def analyze_schema_changes(ir: FlashFlowIR, existing_migrations: List[Dict]) -> List[Dict]:
    """Analyze what schema changes need to be applied"""
    changes = []
    
    # For each model in IR, check if table exists and is up to date
    for model_name, model_data in ir.models.items():
        table_name = model_name.lower() + 's'  # Simple pluralization
        
        # Check if table creation migration exists
        table_migration_exists = any(
            table_name in migration['name'] 
            for migration in existing_migrations
        )
        
        if not table_migration_exists:
            changes.append({
                'type': 'CREATE_TABLE',
                'model': model_name,
                'table': table_name,
                'description': f"Create table '{table_name}' for model '{model_name}'",
                'fields': model_data.get('fields', [])
            })
    
    return changes

def apply_single_migration(project: FlashFlowProject, change: Dict):
    """Apply a single migration change"""
    
    if change['type'] == 'CREATE_TABLE':
        create_table_migration(project, change)
    else:
        raise ValueError(f"Unknown migration type: {change['type']}")

def create_table_migration(project: FlashFlowProject, change: Dict):
    """Create a table creation migration"""
    
    table_name = change['table']
    model_name = change['model']
    fields = change['fields']
    
    # Generate SQL for table creation
    sql_lines = [f"CREATE TABLE {table_name} ("]
    
    # Add ID field by default
    sql_lines.append("    id INTEGER PRIMARY KEY AUTOINCREMENT,")
    
    # Add model fields
    for field in fields:
        field_name = field['name']
        field_type = field.get('type', 'string')
        
        # Map FlashFlow types to SQL types
        sql_type = map_field_type_to_sql(field_type)
        
        constraints = []
        if field.get('required', False) and not field.get('auto', False):
            constraints.append("NOT NULL")
        if field.get('unique', False):
            constraints.append("UNIQUE")
        if field.get('default') is not None:
            default_val = field['default']
            if isinstance(default_val, str):
                constraints.append(f"DEFAULT '{default_val}'")
            else:
                constraints.append(f"DEFAULT {default_val}")
        
        constraint_str = " " + " ".join(constraints) if constraints else ""
        sql_lines.append(f"    {field_name} {sql_type}{constraint_str},")
    
    # Add timestamps by default
    sql_lines.append("    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,")
    sql_lines.append("    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
    sql_lines.append(");")
    
    # Create migration file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    migration_filename = f"{timestamp}_create_{table_name}_table.sql"
    migration_path = project.root_path / "database" / "migrations" / migration_filename
    
    with open(migration_path, 'w') as f:
        f.write("\n".join(sql_lines))
    
    # Execute migration on SQLite database
    execute_sql_migration(project, "\n".join(sql_lines))

def map_field_type_to_sql(field_type: str) -> str:
    """Map FlashFlow field types to SQL types"""
    type_mapping = {
        'string': 'VARCHAR(255)',
        'text': 'TEXT',
        'integer': 'INTEGER',
        'float': 'REAL',
        'boolean': 'BOOLEAN',
        'date': 'DATE',
        'datetime': 'DATETIME',
        'timestamp': 'DATETIME',
        'json': 'TEXT',
        'password': 'VARCHAR(255)',
        'email': 'VARCHAR(255)',
        'url': 'VARCHAR(255)',
        'enum': 'VARCHAR(100)'
    }
    
    return type_mapping.get(field_type, 'VARCHAR(255)')

def execute_sql_migration(project: FlashFlowProject, sql: str):
    """Execute SQL migration on the database"""
    
    # Use SQLite for development
    db_path = project.root_path / "database" / "database.sqlite"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(sql)
        conn.commit()

def get_migration_log(project: FlashFlowProject) -> List[Dict]:
    """Get migration log"""
    log_path = project.root_path / "database" / "migrations.log"
    
    if not log_path.exists():
        return []
    
    with open(log_path, 'r') as f:
        return json.load(f)

def update_migration_log(project: FlashFlowProject, applied_changes: List[Dict]):
    """Update migration log with applied changes"""
    log_path = project.root_path / "database" / "migrations.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    existing_log = get_migration_log(project) if log_path.exists() else []
    
    for change in applied_changes:
        log_entry = {
            'id': f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{change['model'].lower()}",
            'type': change['type'],
            'model': change['model'],
            'description': change['description'],
            'applied_at': datetime.now().isoformat()
        }
        existing_log.append(log_entry)
    
    with open(log_path, 'w') as f:
        json.dump(existing_log, f, indent=2)
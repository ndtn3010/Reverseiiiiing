from __future__ import annotations

import asyncio
import json
import logging

import typer
from rich.console import Console
from rich.table import Table

from .config import load_config
from .meta import db as dbmod
from .meta import patch_watcher

app = typer.Typer(help="Reverseiiiiing — TFT auto-player AI control CLI")
console = Console()


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


@app.command("init-db")
def init_db(
    config: str = typer.Option("config.yaml", "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Create the SQLite schema (idempotent)."""
    _setup_logging(verbose)
    cfg = load_config(config)
    dbmod.init_db(cfg.db.path)
    console.print(f"[green]db initialised[/] at {cfg.db.path}")


@app.command("refresh")
def refresh(
    config: str = typer.Option("config.yaml", "--config", "-c"),
    force: bool = typer.Option(False, "--force", "-f", help="Refresh even if versions match"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Pull CommunityDragon data and upsert into the DB."""
    import httpx
    _setup_logging(verbose)
    cfg = load_config(config)
    dbmod.init_db(cfg.db.path)
    try:
        result = asyncio.run(patch_watcher.refresh_if_changed(cfg, force=force))
    except (httpx.ProxyError, httpx.ConnectError, httpx.TimeoutException) as e:
        console.print(f"[red]network error:[/] {type(e).__name__}: {e}")
        console.print(
            "[yellow]tip: raw.communitydragon.org must be reachable. "
            "Run this on a machine with open HTTPS egress, not in a locked-down sandbox.[/]"
        )
        raise typer.Exit(code=2)
    console.print_json(data=result)


@app.command("status")
def status(
    config: str = typer.Option("config.yaml", "--config", "-c"),
) -> None:
    """Show DB row counts + latest patch."""
    cfg = load_config(config)
    with dbmod.connect(cfg.db.path) as conn:
        counts = dbmod.counts(conn)
        latest = conn.execute(
            "SELECT version, cdragon_hash, detected_at FROM patches "
            "ORDER BY detected_at DESC LIMIT 1"
        ).fetchone()

    tbl = Table(title="DB status", show_header=True)
    tbl.add_column("table")
    tbl.add_column("rows", justify="right")
    for k, v in counts.items():
        tbl.add_row(k, str(v))
    console.print(tbl)
    if latest:
        console.print(
            f"latest patch: [bold]{latest['version']}[/] "
            f"hash={latest['cdragon_hash']} detected_at={latest['detected_at']}"
        )
    else:
        console.print("[yellow]no patch ingested yet — run `rv refresh`[/]")


@app.command("inspect")
def inspect(
    table: str = typer.Argument(..., help="champions | traits | items | augments | wisps | comps"),
    limit: int = typer.Option(10, "--limit", "-n"),
    cost: int | None = typer.Option(None, "--cost", help="filter champions by cost"),
    config: str = typer.Option("config.yaml", "--config", "-c"),
) -> None:
    """Print sample rows from a table."""
    cfg = load_config(config)
    with dbmod.connect(cfg.db.path) as conn:
        if table == "champions" and cost is not None:
            rows = conn.execute(
                "SELECT champ_id, name, cost, hp_1star, ad_1star, mana_max FROM champions "
                "WHERE cost = ? ORDER BY name LIMIT ?",
                (cost, limit),
            ).fetchall()
        elif table == "champions":
            rows = conn.execute(
                "SELECT champ_id, name, cost, hp_1star, ad_1star, mana_max FROM champions "
                "ORDER BY cost, name LIMIT ?",
                (limit,),
            ).fetchall()
        elif table == "traits":
            rows = conn.execute(
                "SELECT trait_id, name, breakpoints_json FROM traits ORDER BY name LIMIT ?",
                (limit,),
            ).fetchall()
        elif table == "items":
            rows = conn.execute(
                "SELECT item_id, name, recipe, is_radiant, is_emblem FROM items "
                "ORDER BY name LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = conn.execute(
                f"SELECT * FROM {table} LIMIT ?",
                (limit,),
            ).fetchall()

    if not rows:
        console.print(f"[yellow]{table}: empty[/]")
        return

    tbl = Table(title=table, show_header=True)
    for key in rows[0].keys():
        tbl.add_column(key)
    for r in rows:
        tbl.add_row(*[str(r[k])[:60] for k in r.keys()])
    console.print(tbl)


@app.command("probe")
def probe(
    config: str = typer.Option("config.yaml", "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Fetch CDragon payload and print a summary (no DB write)."""
    import asyncio as _a
    import httpx
    from .meta import cdragon as _cd
    _setup_logging(verbose)
    cfg = load_config(config)
    try:
        raw = _a.run(_cd.fetch(cfg))
    except (httpx.ProxyError, httpx.ConnectError, httpx.TimeoutException) as e:
        console.print(f"[red]network error:[/] {type(e).__name__}: {e}")
        raise typer.Exit(code=2)
    payload = raw.payload
    top_keys = list(payload.keys())
    set_entry = _cd._find_set(payload, cfg.set.current)
    out = {
        "content_hash": raw.content_hash,
        "top_keys": top_keys,
        "set_found": set_entry is not None,
        "set_keys": list(set_entry.keys()) if set_entry else None,
        "champion_count": len(set_entry.get("champions") or []) if set_entry else 0,
        "trait_count": len(set_entry.get("traits") or []) if set_entry else 0,
        "item_count": len(payload.get("items") or []),
    }
    console.print_json(data=out)


if __name__ == "__main__":
    app()

from __future__ import annotations

from html import escape
from typing import Any


def build_timeline(
    *,
    passport: dict[str, Any],
    certificate: dict[str, Any],
    trace_correlation: dict[str, Any],
    incident_record: dict[str, Any],
    regression_asset: dict[str, Any],
    revalidation: dict[str, Any],
    trust_assessment: dict[str, Any],
) -> list[dict[str, str]]:
    release_id = str(passport.get('release', {}).get('release_id', 'unknown'))
    return [
        {
            'stage': 'System Passport',
            'id': f'passport:{release_id}',
            'status': str(passport.get('assurance', {}).get('overall_status', 'unknown')),
            'detail': 'Release identity, components, security, quality, approval and governance evidence.',
        },
        {
            'stage': 'Release Certificate',
            'id': str(certificate.get('certificate_id', 'unknown')),
            'status': str(certificate.get('status', 'unknown')),
            'detail': 'Deterministic certification derived from the evidence bundle and release controls.',
        },
        {
            'stage': 'Production Trace',
            'id': str(trace_correlation.get('trace_id', 'unknown')),
            'status': 'CORRELATED' if trace_correlation.get('correlated') else 'MISMATCH',
            'detail': 'Runtime behavior is correlated to the certified release, model, prompt, retriever, agent and policy.',
        },
        {
            'stage': 'Incident',
            'id': str(incident_record.get('incident_id', 'unknown')),
            'status': str(incident_record.get('status', 'unknown')).upper(),
            'detail': 'Production issue linked back to the runtime trace and certified configuration.',
        },
        {
            'stage': 'Regression Asset',
            'id': str(regression_asset.get('asset_id', 'unknown')),
            'status': 'CREATED',
            'detail': 'Root cause, reproduction steps, blocking assertions and regression scope captured as reusable evidence.',
        },
        {
            'stage': 'Revalidation',
            'id': str(revalidation.get('revalidation_id', 'unknown')),
            'status': str(revalidation.get('decision', 'unknown')),
            'detail': 'Targeted regression, safety, authorization, rollback readiness and approval determine recovery.',
        },
        {
            'stage': 'Trust Recalculation',
            'id': f"trust:{trust_assessment.get('release_id', release_id)}",
            'status': str(trust_assessment.get('trust_status', 'unknown')),
            'detail': f"Explainable trust score {trust_assessment.get('trust_score', 0)}/100 with hard blockers taking precedence.",
        },
    ]


def render_release_assurance_html(
    *,
    passport: dict[str, Any],
    certificate: dict[str, Any],
    trace_correlation: dict[str, Any],
    incident_record: dict[str, Any],
    regression_asset: dict[str, Any],
    revalidation: dict[str, Any],
    trust_assessment: dict[str, Any],
) -> str:
    timeline = build_timeline(
        passport=passport,
        certificate=certificate,
        trace_correlation=trace_correlation,
        incident_record=incident_record,
        regression_asset=regression_asset,
        revalidation=revalidation,
        trust_assessment=trust_assessment,
    )

    status = escape(str(trust_assessment.get('trust_status', 'unknown')))
    score = int(trust_assessment.get('trust_score', 0))
    release_id = escape(str(trust_assessment.get('release_id', 'unknown')))
    system_id = escape(str(trust_assessment.get('system_id', 'unknown')))
    blockers = trust_assessment.get('hard_blockers', [])
    warnings = trust_assessment.get('warnings', [])
    factors = trust_assessment.get('factors', {})

    cards = []
    for index, item in enumerate(timeline, start=1):
        cards.append(
            "<article class='stage-card'>"
            f"<div class='stage-index'>{index:02d}</div>"
            f"<div><div class='stage-name'>{escape(item['stage'])}</div>"
            f"<div class='stage-id'>{escape(item['id'])}</div>"
            f"<span class='badge'>{escape(item['status'])}</span>"
            f"<p>{escape(item['detail'])}</p></div>"
            "</article>"
        )

    node_rows = []
    for node in trust_assessment.get('nodes', []):
        node_rows.append(
            '<tr>'
            f"<td>{escape(str(node.get('node_type', '')))}</td>"
            f"<td><code>{escape(str(node.get('node_id', '')))}</code></td>"
            f"<td>{escape(str(node.get('status', '')))}</td>"
            f"<td><code>{escape(str(node.get('integrity_sha256') or '—'))}</code></td>"
            '</tr>'
        )

    edge_rows = []
    for edge in trust_assessment.get('edges', []):
        edge_rows.append(
            '<tr>'
            f"<td><code>{escape(str(edge.get('source', '')))}</code></td>"
            f"<td>{escape(str(edge.get('relation', '')))}</td>"
            f"<td><code>{escape(str(edge.get('target', '')))}</code></td>"
            '</tr>'
        )

    factor_rows = ''.join(
        f"<div class='factor'><span>{escape(str(name).replace('_', ' ').title())}</span><strong>{int(value)}</strong></div>"
        for name, value in factors.items()
    )
    blocker_items = ''.join(f"<li>{escape(str(x))}</li>" for x in blockers) or '<li>None</li>'
    warning_items = ''.join(f"<li>{escape(str(x))}</li>" for x in warnings) or '<li>None</li>'

    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<title>AI Release Assurance Timeline — {release_id}</title>
<style>
:root{{--bg:#f7f9fc;--card:#fff;--ink:#10233d;--muted:#637083;--line:#dce4ee;--accent:#1565c0;--teal:#00796b;--warn:#9a6700;--danger:#b42318}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,Segoe UI,Arial,sans-serif;line-height:1.45}}
main{{max-width:1180px;margin:auto;padding:42px 24px 64px}} .eyebrow{{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:800}}
h1{{font-size:42px;line-height:1.08;margin:8px 0 10px}} .subtitle{{color:var(--muted);max-width:850px}}
.hero{{display:grid;grid-template-columns:1.5fr .75fr;gap:24px;margin-top:28px}} .panel,.stage-card{{background:var(--card);border:1px solid var(--line);border-radius:18px;box-shadow:0 8px 28px rgba(16,35,61,.06)}}
.panel{{padding:24px}} .score{{font-size:64px;font-weight:900;letter-spacing:-.04em}} .score small{{font-size:20px;color:var(--muted)}} .status{{font-weight:900;color:var(--teal)}}
.meta{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:18px}} .meta div{{background:#f2f6fb;padding:14px;border-radius:12px}} .meta small{{display:block;color:var(--muted)}}
.timeline{{display:grid;gap:14px;margin:28px 0}} .stage-card{{display:grid;grid-template-columns:58px 1fr;gap:16px;padding:18px 20px;position:relative}} .stage-card:not(:last-child)::after{{content:'';position:absolute;left:48px;bottom:-15px;height:15px;border-left:2px solid var(--line)}}
.stage-index{{width:42px;height:42px;border-radius:12px;background:#e8f1fc;display:grid;place-items:center;font-weight:900;color:var(--accent)}} .stage-name{{font-size:18px;font-weight:850}} .stage-id{{color:var(--muted);font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:12px;margin:2px 0 8px}} .badge{{display:inline-block;padding:4px 9px;border-radius:999px;background:#e9f7f4;color:var(--teal);font-weight:800;font-size:12px}} .stage-card p{{margin:8px 0 0;color:var(--muted)}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:20px}} h2{{margin:0 0 14px;font-size:22px}} ul{{padding-left:20px}} .factor{{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid var(--line)}}
table{{width:100%;border-collapse:collapse;font-size:13px}} th,td{{padding:10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}} th{{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.08em}} code{{font-size:11px;word-break:break-all}}
.section{{margin-top:22px}} .note{{margin-top:24px;padding:16px 18px;border-left:4px solid var(--accent);background:#eef5fd;color:#38506d;border-radius:8px}}
@media(max-width:800px){{.hero,.grid2{{grid-template-columns:1fr}}h1{{font-size:34px}}}}
</style>
</head>
<body><main>
<div class='eyebrow'>Enterprise AI Quality Engineering</div>
<h1>Release Assurance Timeline & Evidence Graph</h1>
<p class='subtitle'>One explainable lifecycle connecting pre-release assurance, certified production configuration, runtime evidence, incident response, regression generation, revalidation and trust recalculation.</p>
<section class='hero'>
<div class='panel'><div class='status'>{status}</div><div class='score'>{score}<small>/100</small></div><div class='meta'><div><small>System</small><strong>{system_id}</strong></div><div><small>Release</small><strong>{release_id}</strong></div></div></div>
<div class='panel'><h2>Trust factors</h2>{factor_rows}</div>
</section>
<section class='timeline'>{''.join(cards)}</section>
<section class='grid2'>
<div class='panel'><h2>Hard blockers</h2><ul>{blocker_items}</ul></div>
<div class='panel'><h2>Warnings & residual risks</h2><ul>{warning_items}</ul></div>
</section>
<section class='panel section'><h2>Evidence nodes</h2><table><thead><tr><th>Type</th><th>ID</th><th>Status</th><th>Integrity SHA-256</th></tr></thead><tbody>{''.join(node_rows)}</tbody></table></section>
<section class='panel section'><h2>Evidence relationships</h2><table><thead><tr><th>Source</th><th>Relationship</th><th>Target</th></tr></thead><tbody>{''.join(edge_rows)}</tbody></table></section>
<div class='note'><strong>Governance rule:</strong> the trust score is explanatory only. Hard blockers always override the numeric score and prevent a release from being represented as trusted.</div>
</main></body></html>"""

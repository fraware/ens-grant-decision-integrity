"""SSRF-safe source capture pipeline.

Capture creates preserved bytes + source-artifact metadata. The offline verifier
(``verify_artifact`` / ``gdi verify-source``) never fetches remote URLs.

Historical ``reference-only`` corpus sources must not be upgraded to byte-verified
merely because a later live capture succeeded.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import socket
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urljoin, urlsplit

from gdi import __version__
from gdi.source.artifact import SourceArtifactError, build_artifact, verify_artifact

TOOL_NAME = "gdi-source-capture"
DEFAULT_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_TIMEOUT_SEC = 15
DEFAULT_MAX_REDIRECTS = 5

BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "localhost.localdomain",
        "metadata.google.internal",
        "metadata",
    }
)


@dataclass(frozen=True)
class CaptureResult:
    artifact: dict[str, Any]
    bytes_path: Path
    artifact_path: Path
    capture_log: dict[str, Any]
    capture_log_path: Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_blocked_ip(address: str) -> bool:
    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        return True
    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
        or ip.version == 4
        and ip in ipaddress.ip_network("169.254.0.0/16")
        or ip.version == 6
        and (
            ip in ipaddress.ip_network("fc00::/7")
            or ip in ipaddress.ip_network("fe80::/10")
            or ip == ipaddress.ip_address("::1")
        )
    )


def assert_safe_url(
    url: str,
    *,
    allow_http: bool = False,
    allow_private: bool = False,
    resolver: Callable[[str], list[str]] | None = None,
) -> None:
    """Reject SSRF-prone URLs. Used before each request and after each redirect."""
    try:
        parsed = urlsplit(url)
    except ValueError as exc:
        raise SourceArtifactError(f"malformed capture URL: {exc}", code="CAP001") from exc
    scheme = parsed.scheme.lower()
    if scheme == "file":
        raise SourceArtifactError("file:// URLs are not allowed for network capture", code="CAP002")
    if scheme not in {"https", "http"}:
        raise SourceArtifactError(f"unsupported capture URL scheme {scheme!r}", code="CAP003")
    if scheme == "http" and not allow_http:
        raise SourceArtifactError("http capture requires explicit --allow-http", code="CAP004")
    host = (parsed.hostname or "").lower()
    if not host:
        raise SourceArtifactError("capture URL missing host", code="CAP005")
    if host in BLOCKED_HOSTNAMES or host.endswith(".localhost"):
        raise SourceArtifactError(f"blocked capture host {host!r}", code="CAP006")
    if allow_private:
        return
    resolve = resolver or _resolve_host_ips
    try:
        addresses = resolve(host)
    except OSError as exc:
        raise SourceArtifactError(f"DNS resolution failed for {host!r}: {exc}", code="CAP007") from exc
    if not addresses:
        raise SourceArtifactError(f"no DNS addresses for host {host!r}", code="CAP007")
    for address in addresses:
        if _is_blocked_ip(address):
            raise SourceArtifactError(
                f"refusing capture to non-public address {address} for host {host!r}",
                code="CAP008",
            )


def _resolve_host_ips(host: str) -> list[str]:
    infos = socket.getaddrinfo(host, None)
    addresses: list[str] = []
    for info in infos:
        addr = info[4][0]
        if addr not in addresses:
            addresses.append(addr)
    return addresses


def content_addressed_paths(out_dir: Path, digest_hex: str) -> tuple[Path, Path]:
    shard = digest_hex[:2]
    leaf = out_dir / "sha256" / shard / digest_hex
    leaf.mkdir(parents=True, exist_ok=True)
    return leaf / "source.bytes", leaf / "source.artifact.json"


def _write_bytes_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)


def _safe_local_file(path: Path, *, root: Path | None = None) -> Path:
    resolved = path.resolve()
    if root is not None:
        root_resolved = root.resolve()
        try:
            resolved.relative_to(root_resolved)
        except ValueError as exc:
            raise SourceArtifactError("local capture path escapes allowed root", code="CAP009") from exc
    if not resolved.is_file():
        raise SourceArtifactError(f"manual-file path is not a regular file: {resolved}", code="CAP010")
    if resolved.is_symlink():
        # resolve() already followed; still reject if original was symlink outside root handled above.
        pass
    return resolved


def store_captured_bytes(
    *,
    out_dir: Path,
    data: bytes,
    artifact_id: str,
    source_uri: str,
    method: str,
    media_type: str,
    resolved_uri: str | None = None,
    http_status: int | None = None,
    content_encoding: str | None = None,
    capture_notes: str | None = None,
    observations: list[str] | None = None,
    capture_log: dict[str, Any] | None = None,
) -> CaptureResult:
    digest_hex = hashlib.sha256(data).hexdigest()
    bytes_path, artifact_path = content_addressed_paths(out_dir, digest_hex)
    if bytes_path.exists():
        existing = bytes_path.read_bytes()
        if existing != data:
            raise SourceArtifactError(
                "content-address collision with different bytes",
                code="CAP011",
            )
    else:
        _write_bytes_atomic(bytes_path, data)

    relative_bytes = str(bytes_path.relative_to(out_dir)).replace("\\", "/")
    artifact = build_artifact(
        artifact_id=artifact_id,
        source_uri=source_uri,
        file_path=bytes_path,
        media_type=media_type,
        method=method,
        tool=TOOL_NAME,
        tool_version=__version__,
        resolved_uri=resolved_uri,
        http_status=http_status,
        stored_path=relative_bytes,
        content_encoding=content_encoding,
        capture_notes=capture_notes,
        observations=observations,
    )
    artifact_path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    log = capture_log or {}
    log_path = artifact_path.with_name("capture.log.json")
    log_path.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    # Offline verify immediately.
    verify_artifact(artifact, bytes_path)
    return CaptureResult(
        artifact=artifact,
        bytes_path=bytes_path,
        artifact_path=artifact_path,
        capture_log=log,
        capture_log_path=log_path,
    )


def capture_manual_file(
    *,
    source_uri: str,
    file_path: Path,
    out_dir: Path,
    artifact_id: str,
    media_type: str = "application/octet-stream",
    allow_root: Path | None = None,
) -> CaptureResult:
    safe = _safe_local_file(file_path, root=allow_root)
    data = safe.read_bytes()
    return store_captured_bytes(
        out_dir=out_dir,
        data=data,
        artifact_id=artifact_id,
        source_uri=source_uri,
        method="manual-file",
        media_type=media_type,
        observations=[f"originalFilename={safe.name}"],
        capture_log={
            "method": "manual-file",
            "capturedAt": _utc_now(),
            "sourceUri": source_uri,
            "originalPath": str(safe),
            "nonClaims": [
                "manual-file capture does not invent a public URI",
                "capturedAt is operator metadata, not an anchored timestamp",
            ],
        },
    )


def capture_browser_export(
    *,
    source_uri: str,
    export_path: Path,
    out_dir: Path,
    artifact_id: str,
    media_type: str,
    browser_tool: str,
    browser_version: str,
    allow_root: Path | None = None,
) -> CaptureResult:
    safe = _safe_local_file(export_path, root=allow_root)
    data = safe.read_bytes()
    return store_captured_bytes(
        out_dir=out_dir,
        data=data,
        artifact_id=artifact_id,
        source_uri=source_uri,
        method="browser-export",
        media_type=media_type,
        capture_notes=f"Exported artifact reviewed via {browser_tool} {browser_version}",
        observations=[
            "browser-export bytes are the reviewed export, not necessarily raw HTTP HTML",
            f"browserTool={browser_tool}",
            f"browserVersion={browser_version}",
        ],
        capture_log={
            "method": "browser-export",
            "capturedAt": _utc_now(),
            "sourceUri": source_uri,
            "exportPath": str(safe),
            "browserTool": browser_tool,
            "browserVersion": browser_version,
            "nonClaims": [
                "Export hash is not a hash of the origin server's raw HTML unless that response was captured separately."
            ],
        },
    )


def capture_git_blob(
    *,
    source_uri: str,
    blob_path: Path,
    out_dir: Path,
    artifact_id: str,
    repository: str,
    commit_sha: str,
    blob_sha: str,
    media_type: str = "application/octet-stream",
    allow_root: Path | None = None,
) -> CaptureResult:
    safe = _safe_local_file(blob_path, root=allow_root)
    data = safe.read_bytes()
    return store_captured_bytes(
        out_dir=out_dir,
        data=data,
        artifact_id=artifact_id,
        source_uri=source_uri,
        method="git-blob",
        media_type=media_type,
        observations=[
            f"repository={repository}",
            f"commitSha={commit_sha}",
            f"blobSha={blob_sha}",
        ],
        capture_log={
            "method": "git-blob",
            "capturedAt": _utc_now(),
            "sourceUri": source_uri,
            "repository": repository,
            "commitSha": commit_sha,
            "blobSha": blob_sha,
            "nonClaims": [
                "A mutable branch URL is not equivalent to an immutable commit/blob reference."
            ],
        },
    )


def capture_http(
    *,
    source_uri: str,
    out_dir: Path,
    artifact_id: str,
    allow_http: bool = False,
    allow_private: bool = False,
    max_bytes: int = DEFAULT_MAX_BYTES,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC,
    max_redirects: int = DEFAULT_MAX_REDIRECTS,
    opener: Callable[..., Any] | None = None,
    resolver: Callable[[str], list[str]] | None = None,
) -> CaptureResult:
    """Fetch bytes with redirect revalidation and SSRF controls."""
    current = source_uri
    redirect_chain: list[dict[str, Any]] = []
    crossed_origin = False
    original = urlsplit(source_uri)

    for _ in range(max_redirects + 1):
        assert_safe_url(
            current,
            allow_http=allow_http,
            allow_private=allow_private,
            resolver=resolver,
        )
        request = urllib.request.Request(
            current,
            headers={"User-Agent": f"{TOOL_NAME}/{__version__}", "Accept": "*/*"},
            method="GET",
        )
        try:
            if opener is not None:
                response = opener(request, timeout=timeout_sec)
            else:
                context = ssl.create_default_context()
                response = urllib.request.urlopen(request, timeout=timeout_sec, context=context)
        except urllib.error.HTTPError as exc:
            # Treat 3xx with Location as redirects even via HTTPError in some stacks.
            if 300 <= exc.code < 400 and exc.headers.get("Location"):
                location = exc.headers["Location"]
                nxt = urljoin(current, location)
                prev = urlsplit(current)
                nxt_p = urlsplit(nxt)
                if (prev.scheme, prev.netloc) != (nxt_p.scheme, nxt_p.netloc):
                    crossed_origin = True
                redirect_chain.append(
                    {
                        "from": current,
                        "to": nxt,
                        "status": exc.code,
                        "crossedOrigin": (prev.scheme, prev.netloc) != (nxt_p.scheme, nxt_p.netloc),
                    }
                )
                current = nxt
                continue
            raise SourceArtifactError(f"HTTP capture failed with status {exc.code}", code="CAP012") from exc
        except urllib.error.URLError as exc:
            raise SourceArtifactError(f"HTTP capture network error: {exc}", code="CAP013") from exc

        with response:
            status = getattr(response, "status", None) or response.getcode()
            if 300 <= int(status) < 400:
                location = response.headers.get("Location")
                if not location:
                    raise SourceArtifactError("redirect without Location header", code="CAP014")
                nxt = urljoin(current, location)
                prev = urlsplit(current)
                nxt_p = urlsplit(nxt)
                if (prev.scheme, prev.netloc) != (nxt_p.scheme, nxt_p.netloc):
                    crossed_origin = True
                redirect_chain.append(
                    {
                        "from": current,
                        "to": nxt,
                        "status": int(status),
                        "crossedOrigin": (prev.scheme, prev.netloc) != (nxt_p.scheme, nxt_p.netloc),
                    }
                )
                current = nxt
                continue

            # Re-validate final URL (defense in depth).
            assert_safe_url(
                current,
                allow_http=allow_http,
                allow_private=allow_private,
                resolver=resolver,
            )
            chunks: list[bytes] = []
            total = 0
            while True:
                chunk = response.read(64 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise SourceArtifactError(
                        f"response exceeds max_bytes={max_bytes}; partial body discarded",
                        code="CAP015",
                    )
                chunks.append(chunk)
            data = b"".join(chunks)
            media_type = response.headers.get_content_type() or "application/octet-stream"
            charset = response.headers.get_content_charset()
            encoding = response.headers.get("Content-Encoding")
            etag = response.headers.get("ETag")
            last_modified = response.headers.get("Last-Modified")
            final = urlsplit(current)
            if (original.scheme, original.netloc) != (final.scheme, final.netloc):
                crossed_origin = True
            observations = [
                f"redirectCount={len(redirect_chain)}",
                f"crossedOrigin={str(crossed_origin).lower()}",
            ]
            if charset:
                observations.append(f"declaredCharset={charset}")
            if etag:
                observations.append(f"etag={etag}")
            if last_modified:
                observations.append(f"lastModified={last_modified}")
            log = {
                "method": "http",
                "capturedAt": _utc_now(),
                "requestedUri": source_uri,
                "resolvedUri": current,
                "redirectChain": redirect_chain,
                "httpStatus": int(status),
                "mediaType": media_type,
                "contentEncoding": encoding,
                "byteLength": len(data),
                "contentHash": "sha256:" + hashlib.sha256(data).hexdigest(),
                "userAgent": f"{TOOL_NAME}/{__version__}",
                "crossedOrigin": crossed_origin,
                "nonClaims": [
                    "HTTP capture metadata is transport observation, not proof of authority or publication time.",
                    "Redirect destinations are not silently treated as equivalent to the cited policy URI.",
                ],
            }
            return store_captured_bytes(
                out_dir=out_dir,
                data=data,
                artifact_id=artifact_id,
                source_uri=source_uri,
                method="http",
                media_type=media_type,
                resolved_uri=current if current != source_uri else None,
                http_status=int(status),
                content_encoding=encoding,
                observations=observations,
                capture_log=log,
            )

    raise SourceArtifactError(f"exceeded max_redirects={max_redirects}", code="CAP016")

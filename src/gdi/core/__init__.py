from gdi.core import conformance as _conformance

Finding = _conformance.Finding
validate_record = _conformance.validate_record
check_schema_02_extensions = getattr(_conformance, "check_schema_02_extensions", None)

__all__ = [name for name in dir(_conformance) if not name.startswith("_")]

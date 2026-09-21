"""Filament Module: ISO-style spec artifacts.

This package ships the module's own data — its manifest, skeletons, emitted
schemas and mappings — and nothing belonging to another repository. It used to
ship a copy of filament-core-service's FR-035 module-manifest schema as public
package data, so that sibling module repositories could validate their manifests
against it. That is removed (PLAT-902): a copy is a copy however it is
distributed, and one redistributed from here gave four repositories a gate that
compared a manifest to bytes this repository maintained. A module proves
conformance to FR-035 by activating against the service that applies it.
"""


def hello():
    return "Hello, World!"

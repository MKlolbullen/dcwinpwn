"""
Base definitions for linWinPwn-next modules.

Each module should inherit from `Module` and implement the `run` method.
Modules are responsible for:
  - Declaring their `name` and `supported_auth` set.
  - Accepting a Session and Target object.
  - Returning a ModuleResult with nodes/edges for the graph.

This file also provides:
  - A registry for auto-discovery of modules.
  - Common error/result helpers.
"""

from abc import ABC, abstractmethod
from typing import Set, Type, Dict, Any
from core.types import Session, Target, ModuleResult


class Module(ABC):
    """
    Abstract base class for all modules.
    """

    #: Unique name of the module (e.g. "ldap_enum")
    name: str = "base"

    #: Supported authentication methods (password, ntlm, aes, ticket, cert, null)
    supported_auth: Set[str] = set()

    def __init__(self, **kwargs: Any):
        """
        Optional constructor for module-specific configuration.
        """
        self.config = kwargs

    @abstractmethod
    async def run(self, session: Session, target: Target) -> ModuleResult:
        """
        Execute the module against a given target with a given session.

        Args:
            session: Authentication/session context.
            target: Target host or service.

        Returns:
            ModuleResult: structured result with nodes/edges and artifacts.
        """
        raise NotImplementedError

    def check_auth_supported(self, method: str) -> bool:
        """
        Check if the given authentication method is supported by this module.
        """
        return method in self.supported_auth

    def __repr__(self) -> str:
        return f"<Module {self.name} supports={self.supported_auth}>"

    def fail_result(self, target: Target, reason: str) -> ModuleResult:
        """
        Convenience helper to return a failed ModuleResult.
        """
        return ModuleResult(
            module=self.name,
            tool=self.name,
            target=target.host,
            status="tool_error",
            started_at="",
            ended_at="",
            stdout_path="",
            stderr_path=reason,
            artifacts=[],
            nodes=[],
            edges=[]
        )


# --- Registry for modules ---

_MODULE_REGISTRY: Dict[str, Type[Module]] = {}


def register_module(cls: Type[Module]) -> Type[Module]:
    """
    Decorator to register a Module subclass into the registry.
    Usage:

        @register_module
        class LdapEnum(Module):
            ...
    """
    if not issubclass(cls, Module):
        raise TypeError("Only Module subclasses can be registered")
    if not getattr(cls, "name", None):
        raise ValueError("Module must define a name")
    _MODULE_REGISTRY[cls.name] = cls
    return cls


def get_module(name: str) -> Type[Module]:
    """
    Retrieve a module class by name.
    """
    return _MODULE_REGISTRY[name]


def list_modules() -> Dict[str, Type[Module]]:
    """
    Return the full registry of modules.
    """
    return dict(_MODULE_REGISTRY)
